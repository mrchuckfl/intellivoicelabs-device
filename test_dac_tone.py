#!/usr/bin/env python3
"""Generate test tone and output to DAC8532."""
import spidev
import math
import time
import sys

def generate_sine_wave(frequency, sample_rate, duration, amplitude=0.5):
    """Generate sine wave samples."""
    samples = []
    num_samples = int(sample_rate * duration)
    
    for i in range(num_samples):
        # Generate sine wave
        t = i / sample_rate
        value = math.sin(2 * math.pi * frequency * t)
        
        # Scale to 0-1 range with amplitude control
        scaled = (value * amplitude + 1.0) / 2.0
        
        # Convert to 16-bit DAC value (0-65535)
        dac_value = int(scaled * 65535)
        
        # Clamp to valid range
        dac_value = max(0, min(65535, dac_value))
        
        samples.append(dac_value)
    
    return samples

def send_to_dac(spi, value):
    """Send 16-bit value to DAC8532 channel A."""
    # DAC8532 command format: [Command] [MSB] [LSB]
    # Command 0x00 = Write to DAC A
    msb = (value >> 8) & 0xFF
    lsb = value & 0xFF
    spi.writebytes([0x00, msb, lsb])

def test_tone(frequency=440, duration=3, amplitude=0.5, sample_rate=44100):
    """Generate and play test tone through DAC."""
    
    print("=" * 60)
    print("DAC8532 Test Tone Generator")
    print("=" * 60)
    print()
    print(f"Frequency: {frequency} Hz")
    print(f"Duration: {duration} seconds")
    print(f"Amplitude: {amplitude * 100:.0f}%")
    print(f"Sample rate: {sample_rate} Hz")
    print()
    
    try:
        # Open SPI
        spi = spidev.SpiDev()
        spi.open(10, 0)  # Bus 10, device 0
        spi.max_speed_hz = 1000000  # 1 MHz
        spi.mode = 1
        
        print("✓ SPI opened successfully")
        print()
        print("Generating sine wave...")
        
        # Generate samples
        samples = generate_sine_wave(frequency, sample_rate, duration, amplitude)
        
        print(f"Generated {len(samples)} samples")
        print()
        print("Playing tone... (Press Ctrl+C to stop early)")
        print()
        
        # Send samples to DAC
        start_time = time.time()
        samples_sent = 0
        
        try:
            for sample in samples:
                send_to_dac(spi, sample)
                
                # Maintain sample rate timing
                samples_sent += 1
                if samples_sent % 1000 == 0:
                    elapsed = time.time() - start_time
                    expected = samples_sent / sample_rate
                    if elapsed < expected:
                        time.sleep(expected - elapsed)
                
            elapsed = time.time() - start_time
            print(f"✓ Tone playback complete ({elapsed:.2f} seconds)")
            
        except KeyboardInterrupt:
            print()
            print("Stopped by user")
        
        # Return to mid-scale (quiet)
        print()
        print("Returning DAC to mid-scale (0V)...")
        send_to_dac(spi, 0x8000)  # Mid-scale = 0V
        
        spi.close()
        
        print()
        print("=" * 60)
        print("✓ Test complete")
        print("=" * 60)
        return True
        
    except FileNotFoundError:
        print("✗ SPI device not found")
        print("  Check if SPI is enabled and device is connected")
        return False
    except PermissionError:
        print("✗ Permission denied")
        print("  Add user to 'spi' group: sudo usermod -a -G spi $USER")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def continuous_tone(frequency=440, amplitude=0.5, sample_rate=44100):
    """Generate continuous tone until interrupted."""
    
    print("=" * 60)
    print("DAC8532 Continuous Tone Generator")
    print("=" * 60)
    print()
    print(f"Frequency: {frequency} Hz")
    print(f"Amplitude: {amplitude * 100:.0f}%")
    print(f"Sample rate: {sample_rate} Hz")
    print()
    print("Playing continuous tone... (Press Ctrl+C to stop)")
    print()
    
    try:
        spi = spidev.SpiDev()
        spi.open(10, 0)
        spi.max_speed_hz = 1000000
        spi.mode = 1
        
        print("✓ SPI opened, starting tone...")
        
        sample_period = 1.0 / sample_rate
        start_time = time.time()
        sample_count = 0
        
        try:
            while True:
                t = sample_count / sample_rate
                value = math.sin(2 * math.pi * frequency * t)
                scaled = (value * amplitude + 1.0) / 2.0
                dac_value = int(scaled * 65535)
                dac_value = max(0, min(65535, dac_value))
                
                send_to_dac(spi, dac_value)
                
                sample_count += 1
                
                # Maintain timing
                expected_time = start_time + (sample_count * sample_period)
                current_time = time.time()
                if current_time < expected_time:
                    time.sleep(expected_time - current_time)
                    
        except KeyboardInterrupt:
            print()
            print("Stopping...")
        
        # Return to mid-scale
        send_to_dac(spi, 0x8000)
        spi.close()
        
        print("✓ Stopped, DAC set to mid-scale")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate test tone on DAC8532')
    parser.add_argument('-f', '--frequency', type=int, default=440,
                        help='Frequency in Hz (default: 440)')
    parser.add_argument('-d', '--duration', type=float, default=3.0,
                        help='Duration in seconds (default: 3.0)')
    parser.add_argument('-a', '--amplitude', type=float, default=0.5,
                        help='Amplitude 0.0-1.0 (default: 0.5)')
    parser.add_argument('-r', '--sample-rate', type=int, default=44100,
                        help='Sample rate in Hz (default: 44100)')
    parser.add_argument('-c', '--continuous', action='store_true',
                        help='Play continuous tone (until Ctrl+C)')
    
    args = parser.parse_args()
    
    if args.continuous:
        success = continuous_tone(args.frequency, args.amplitude, args.sample_rate)
    else:
        success = test_tone(args.frequency, args.duration, args.amplitude, args.sample_rate)
    
    sys.exit(0 if success else 1)

