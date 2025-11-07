#!/usr/bin/env python3
"""Test audio passthrough: record from input and play to output."""
import pyaudio
import numpy as np
import time
import sys

def find_hifiberry_devices(pa):
    """Find HiFiBerry input and output device indices."""
    input_device = None
    output_device = None
    
    print("Searching for HiFiBerry devices...")
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if 'hifiberry' in info['name'].lower() or 'sndrpihifiberry' in info['name'].lower():
            if info['maxInputChannels'] > 0:
                input_device = i
                print(f"  ✓ Input: Device {i} - {info['name']}")
            if info['maxOutputChannels'] > 0:
                output_device = i
                print(f"  ✓ Output: Device {i} - {info['name']}")
    
    return input_device, output_device

def test_passthrough(duration=5, sample_rate=44100, use_right_channel=True):
    """Test audio passthrough: record and play simultaneously."""
    
    print("=" * 60)
    print("Audio Passthrough Test")
    print("=" * 60)
    print()
    print(f"Duration: {duration} seconds")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Input channel: {'RIGHT (mono)' if use_right_channel else 'LEFT'}")
    print()
    
    try:
        pa = pyaudio.PyAudio()
        
        # Find devices
        input_device, output_device = find_hifiberry_devices(pa)
        
        if input_device is None:
            print("✗ HiFiBerry input device not found")
            pa.terminate()
            return False
        
        if output_device is None:
            print("✗ HiFiBerry output device not found")
            pa.terminate()
            return False
        
        print()
        print("Opening audio streams...")
        
        # Open input stream (stereo to capture both channels)
        input_stream = pa.open(
            format=pyaudio.paInt16,
            channels=2,  # Record stereo
            rate=sample_rate,
            input=True,
            input_device_index=input_device,
            frames_per_buffer=1024
        )
        
        # Open output stream (mono)
        output_stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,  # Output mono
            rate=sample_rate,
            output=True,
            output_device_index=output_device,
            frames_per_buffer=1024
        )
        
        print("✓ Streams opened successfully")
        print()
        print(f"Recording and playing for {duration} seconds...")
        print("(Speak into the microphone - you should hear it on the output)")
        print()
        
        # Passthrough loop
        start_time = time.time()
        samples_processed = 0
        max_level = 0
        
        try:
            while time.time() - start_time < duration:
                # Read from input
                input_data = input_stream.read(1024, exception_on_overflow=False)
                
                # Convert to numpy array
                samples = np.frombuffer(input_data, dtype=np.int16)
                
                # Extract the appropriate channel (right channel = index 1)
                if use_right_channel:
                    mono_samples = samples[1::2]  # Right channel
                else:
                    mono_samples = samples[0::2]  # Left channel
                
                # Track max level
                max_level = max(max_level, np.max(np.abs(mono_samples)))
                
                # Write to output
                output_stream.write(mono_samples.tobytes())
                
                samples_processed += len(mono_samples)
                
                # Show progress
                elapsed = time.time() - start_time
                if int(elapsed) != int(elapsed - 0.1):
                    progress = min(100, (elapsed / duration) * 100)
                    level_db = 20 * np.log10(max_level / 32767.0) if max_level > 0 else -60
                    print(f"  {progress:.0f}% | Level: {level_db:6.1f} dB", end='\r')
        
        except KeyboardInterrupt:
            print()
            print("Stopped by user")
        
        input_stream.stop_stream()
        output_stream.stop_stream()
        input_stream.close()
        output_stream.close()
        
        elapsed = time.time() - start_time
        level_db = 20 * np.log10(max_level / 32767.0) if max_level > 0 else -60
        
        print()
        print(f"✓ Passthrough complete ({elapsed:.2f} seconds)")
        print(f"  Samples processed: {samples_processed}")
        print(f"  Max level: {max_level} ({level_db:.1f} dB)")
        print()
        
        pa.terminate()
        
        print("=" * 60)
        if level_db > -40:
            print("✓✓✓ Audio passthrough working! ✓✓✓")
        elif level_db > -60:
            print("✓ Audio passthrough working (low signal)")
        else:
            print("⚠ Passthrough working but no signal detected")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test audio passthrough')
    parser.add_argument('-d', '--duration', type=float, default=5.0,
                        help='Duration in seconds (default: 5.0)')
    parser.add_argument('-r', '--sample-rate', type=int, default=44100,
                        help='Sample rate in Hz (default: 44100)')
    parser.add_argument('--left', action='store_true',
                        help='Use left channel instead of right')
    
    args = parser.parse_args()
    
    success = test_passthrough(args.duration, args.sample_rate, not args.left)
    sys.exit(0 if success else 1)

