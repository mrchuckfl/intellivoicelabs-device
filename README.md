# IntelliVoice Microphone Converter (Raspberry Pi 5)

This repository contains the starter framework, configuration, and technical specification for the IntelliVoice Microphone Converter prototype.

## Features
- Real-time mic capture via ADC (ADS1256) and playback via DAC (DAC8532)
- BYPASS/CONVERT modes with physical momentary switches
- Language cycling button hook
- 1.3" SSD1306 OLED status display (mode, language, basic VU)
- LED ring indicators (bypass/convert)
- Threaded audio pipeline and GPIO/display controllers
- Hooks for ONNX Runtime voice-conversion model

## Hardware
- Raspberry Pi 5 (8GB) running Ubuntu 24.04 (64-bit)
- High-Precision AD/DA board (ADS1256 + DAC8532) via SPI
- NE5532 preamp between CB mic and ADC
- SSD1306 OLED 128x64 via I²C
- Two momentary buttons (mode, language)
- Two 3.3V LED rings
- Optional PTT GPIO input

## Quick Start
1. Enable I²C and SPI on the Pi.
2. Install dependencies:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-pyaudio python3-numpy python3-luma.oled python3-gpiozero python3-onnxruntime alsa-utils
   pip3 install -r requirements.txt
   ```
3. Run the app:
   ```bash
   sudo python3 main.py
   ```
   (GPIO/ALSA access may require sudo depending on your setup.)

## Configuration
- `config.json` holds pins, sample rates, buffer sizes, and feature toggles.
- Edit `config.json` to match your wiring or language defaults.

## Notes
- Voice conversion is a placeholder; integrate your ONNX model in `voice/engine.py` later.
- If your LED rings draw >20mA, drive them with a transistor/MOSFET and suitable resistor.

## License
Internal prototype — IntelliVoice Labs.
