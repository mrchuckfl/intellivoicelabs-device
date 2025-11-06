#!/usr/bin/env python3
"""Test audio output on HiFiBerry DAC+ADC Pro."""
import pyaudio
import numpy as np
import math
import time
import sys

def generate_tone(frequency=440, duration=2, sample_rate=44100, amplitude=0.3):
    """Generate sine wave tone."""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        value = math.sin(2 * math.pi * frequency * t) * amplitude
        # Convert to 16-bit integer
        sample = int(value * 32767)
        samples.append(sample)
    
    return np.array(samples, dtype=np.int16)

def find_hifiberry_device(pa):
    """Find HiFiBerry device index."""
    hifiberry_index = None
    
    print("Searching for HiFiBerry device...")
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if 'hifiberry' in info['name'].lower() or 'sndrpihifiberry' in info['name'].lower():
            print(f"  ✓ Found: Device {i} - {info['name']}")
            print(f"    Max output channels: {info['maxOutputChannels']}")
            print(f"    Default sample rate: {info['defaultSampleRate']}")
            hifiberry_index = i
            break
    
    return hifiberry_index

def test_audio_output(frequency=440, duration=3, amplitude=0.3, sample_rate=44100):
    """Test audio output through HiFiBerry."""
    
    print("=" * 60)
    print("HiFiBerry Audio Output Test")
    print("=" * 60)
    print()
    print(f"Frequency: {frequency} Hz")
    print(f"Duration: {duration} seconds")
    print(f"Amplitude: {amplitude * 100:.0f}%")
    print(f"Sample rate: {sample_rate} Hz")
    print()
    
    try:
        pa = pyaudio.PyAudio()
        
        # Find HiFiBerry device
        device_index = find_hifiberry_device(pa)
        
        if device_index is None:
            print("✗ HiFiBerry device not found in PyAudio devices")
            print()
            print("Available devices:")
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info['maxOutputChannels'] > 0:
                    print(f"  {i}: {info['name']}")
            pa.terminate()
            return False
        
        print()
        print("Generating test tone...")
        
        # Generate tone
        samples = generate_tone(frequency, duration, sample_rate, amplitude)
        
        print(f"Generated {len(samples)} samples")
        print()
        print("Playing tone through HiFiBerry...")
        print("(You should hear a tone on the output)")
        print()
        
        # Open stream
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True,
            output_device_index=device_index,
            frames_per_buffer=1024
        )
        
        # Play audio
        start_time = time.time()
        stream.write(samples.tobytes())
        stream.stop_stream()
        stream.close()
        elapsed = time.time() - start_time
        
        pa.terminate()
        
        print(f"✓ Audio playback complete ({elapsed:.2f} seconds)")
        print()
        print("=" * 60)
        print("✓ Test complete - Did you hear the tone?")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test HiFiBerry audio output')
    parser.add_argument('-f', '--frequency', type=int, default=440,
                        help='Frequency in Hz (default: 440)')
    parser.add_argument('-d', '--duration', type=float, default=3.0,
                        help='Duration in seconds (default: 3.0)')
    parser.add_argument('-a', '--amplitude', type=float, default=0.3,
                        help='Amplitude 0.0-1.0 (default: 0.3)')
    parser.add_argument('-r', '--sample-rate', type=int, default=44100,
                        help='Sample rate in Hz (default: 44100)')
    
    args = parser.parse_args()
    
    success = test_audio_output(args.frequency, args.duration, args.amplitude, args.sample_rate)
    sys.exit(0 if success else 1)

