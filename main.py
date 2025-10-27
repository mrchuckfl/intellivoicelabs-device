#!/usr/bin/env python3
import os
import sys
import time
import json
import queue
import threading
import logging
from datetime import datetime

import numpy as np

# GPIO / Display
from gpiozero import Button, LED
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306

# Audio
import pyaudio

# Optional AI (placeholder)
try:
    import onnxruntime as ort
except Exception:
    ort = None


class StateManager:
    def __init__(self, config):
        self.lock = threading.Lock()
        self.mode = config["modes"].get("default_mode", "convert")
        self.languages = config["modes"].get("languages", ["EN"])
        self.language_index = 0
        self.running = True
        self.level_rms = 0.0
        self.latency_ms = 0.0
        self.last_switch = time.time()

    def toggle_mode(self):
        with self.lock:
            self.mode = "bypass" if self.mode == "convert" else "convert"
            self.last_switch = time.time()

    def next_language(self):
        with self.lock:
            self.language_index = (self.language_index + 1) % len(self.languages)

    def get_snapshot(self):
        with self.lock:
            return {
                "mode": self.mode,
                "language": self.languages[self.language_index],
                "level_rms": self.level_rms,
                "latency_ms": self.latency_ms,
            }


class OLEDDisplay:
    def __init__(self, cfg):
        self.enabled = cfg["display"].get("enabled", True)
        if not self.enabled:
            self.device = None
            return
        try:
            # Try different i2c ports to find the OLED
            port = cfg["display"].get("i2c_port", 13)
            address = cfg["display"].get("i2c_address", 60)
            # Address is specified in decimal in config (60 = 0x3C)
            serial = i2c(port=port, address=address)
            self.device = ssd1306(serial, width=cfg["display"].get("width", 128), height=cfg["display"].get("height", 64))
        except Exception as e:
            print(f"Warning: OLED display initialization failed: {e}")
            self.device = None

    def draw_text(self, lines):
        if not self.device:
            return
        # Minimal text renderer
        from PIL import Image, ImageDraw, ImageFont
        image = Image.new("1", (self.device.width, self.device.height))
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        y = 0
        for line in lines:
            draw.text((0, y), line, fill=255, font=font)
            y += 12
        self.device.display(image)


class GPIOController:
    def __init__(self, cfg, state: StateManager):
        self.state = state
        try:
            pull = None  # gpiozero handles pulls internally if needed
            self.btn_bypass = Button(cfg["gpio"]["bypass_button"], pull_up=cfg["gpio"].get("pullups", False))
            self.btn_lang = Button(cfg["gpio"]["language_button"], pull_up=cfg["gpio"].get("pullups", False))
            self.led_bypass = LED(cfg["gpio"]["led_bypass"])
            self.led_convert = LED(cfg["gpio"]["led_convert"])
            self.ptt = Button(cfg["gpio"]["ptt_input"], pull_up=cfg["gpio"].get("pullups", False))

            self.btn_bypass.when_pressed = self._on_bypass
            self.btn_lang.when_pressed = self._on_language
        except Exception as e:
            print(f"Warning: GPIO initialization failed: {e}")
            self.btn_bypass = None
            self.btn_lang = None
            self.led_bypass = None
            self.led_convert = None
            self.ptt = None

    def _on_bypass(self):
        self.state.toggle_mode()

    def _on_language(self):
        self.state.next_language()

    def update_leds(self):
        if self.led_bypass is None or self.led_convert is None:
            return
        snap = self.state.get_snapshot()
        self.led_bypass.value = 1 if snap["mode"] == "bypass" else 0
        self.led_convert.value = 1 if snap["mode"] == "convert" else 0

    def ptt_active(self):
        # Active when button is pressed (adjust if your PTT is active-low)
        if self.ptt is None:
            return False
        return self.ptt.is_pressed


class AudioEngine:
    def __init__(self, cfg, state: StateManager):
        self.cfg = cfg
        self.state = state
        self.q_in = queue.Queue(maxsize=8)
        self.q_out = queue.Queue(maxsize=8)
        self.pa = None
        self.stream_in = None
        self.stream_out = None
        
        try:
            self.pa = pyaudio.PyAudio()
            self.stream_in = self.pa.open(
                format=pyaudio.paInt16,
                channels=cfg["audio"]["channels"],
                rate=cfg["audio"]["sample_rate"],
                input=True,
                frames_per_buffer=cfg["audio"]["frames_per_buffer"],
                input_device_index=None,  # adjust if necessary
            )
            self.stream_out = self.pa.open(
                format=pyaudio.paInt16,
                channels=cfg["audio"]["channels"],
                rate=cfg["audio"]["sample_rate"],
                output=True,
                frames_per_buffer=cfg["audio"]["frames_per_buffer"],
                output_device_index=None,  # adjust if necessary
            )
        except Exception as e:
            print(f"Warning: Audio initialization failed: {e}")
            self.pa = None
            self.stream_in = None
            self.stream_out = None

    def start(self):
        self.t_in = threading.Thread(target=self._reader, daemon=True)
        self.t_proc = threading.Thread(target=self._processor, daemon=True)
        self.t_out = threading.Thread(target=self._writer, daemon=True)
        self.t_in.start()
        self.t_proc.start()
        self.t_out.start()

    def _reader(self):
        if self.stream_in is None:
            return
        while True:
            if not self.state.running:
                break
            try:
                data = self.stream_in.read(self.cfg["audio"]["frames_per_buffer"], exception_on_overflow=False)
                # RMS level for VU
                pcm = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                rms = float(np.sqrt(np.mean(np.square(pcm))) / 32768.0)
                self.state.level_rms = rms
                try:
                    self.q_in.put_nowait((time.time(), data))
                except queue.Full:
                    pass  # drop if full
            except Exception as e:
                print(f"Error in audio reader: {e}")
                time.sleep(0.1)

    def _processor(self):
        # Optional: initialize ONNX session
        session = None
        if ort is not None:
            try:
                session = ort.InferenceSession("voice_converter.onnx", providers=['CPUExecutionProvider'])
            except Exception:
                session = None

        while True:
            if not self.state.running:
                break
            try:
                t0, data = self.q_in.get(timeout=0.1)
            except queue.Empty:
                continue

            snap = self.state.get_snapshot()
            if snap["mode"] == "bypass":
                out = data
            else:
                # Placeholder conversion (identity); integrate your model here
                out = self._convert_identity(data, session)

            try:
                self.q_out.put_nowait((t0, out))
            except queue.Full:
                pass

    def _convert_identity(self, data, session):
        # TODO: Replace with mel/vocoder pipeline using `session`
        return data

    def _writer(self):
        if self.stream_out is None:
            return
        while True:
            if not self.state.running:
                break
            try:
                t0, data = self.q_out.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                self.stream_out.write(data)
                self.state.latency_ms = (time.time() - t0) * 1000.0
            except Exception as e:
                print(f"Error in audio writer: {e}")
                time.sleep(0.1)

    def stop(self):
        self.state.running = False
        time.sleep(0.2)
        if self.stream_in:
            try:
                self.stream_in.stop_stream()
                self.stream_in.close()
            except Exception:
                pass
        if self.stream_out:
            try:
                self.stream_out.stop_stream()
                self.stream_out.close()
            except Exception:
                pass
        if self.pa:
            try:
                self.pa.terminate()
            except Exception:
                pass


def load_config():
    with open("config.json") as f:
        return json.load(f)


def setup_logging(cfg):
    logging.basicConfig(
        level=getattr(logging, cfg["logging"].get("level", "INFO")),
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def main():
    cfg = load_config()
    setup_logging(cfg)

    state = StateManager(cfg)

    display = OLEDDisplay(cfg)

    gpioctl = GPIOController(cfg, state)

    audio = AudioEngine(cfg, state)
    audio.start()

    try:
        while True:
            # Periodic status refresh
            gpioctl.update_leds()
            snap = state.get_snapshot()
            lines = [
                f"Mode: {snap['mode']}",
                f"Lang: {snap['language']}",
                f"VU: {snap['level_rms']:.3f}",
                f"Lat: {snap['latency_ms']:.1f} ms",
            ]
            display.draw_text(lines)
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        audio.stop()


if __name__ == "__main__":
    main()
