#!/usr/bin/env python3
"""Test audio input on HiFiBerry DAC+ADC Pro."""
import pyaudio
import numpy as np
import time
import sys

def find_hifiberry_input_device(pa):
    """Find HiFiBerry input device index."""
    hifiberry_index = None
    
    print("Searching for HiFiBerry input device...")
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if 'hifiberry' in info['name'].lower() or 'sndrpihifiberry' in info['name'].lower():
            if info['maxInputChannels'] > 0:
                print(f"  ✓ Found input: Device {i} - {info['name']}")
                print(f"    Max input channels: {info['maxInputChannels']}")
                print(f"    Default sample rate: {info['defaultSampleRate']}")
                hifiberry_index = i
                break
    
    return hifiberry_index

def test_audio_input(duration=3, sample_rate=44100, channels=1):
    """Test audio input from HiFiBerry."""
    
    print("=" * 60)
    print("HiFiBerry Audio Input Test")
    print("=" * 60)
    print()
    print(f"Duration: {duration} seconds")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Channels: {channels}")
    print()
    
    try:
        pa = pyaudio.PyAudio()
        
        # Find HiFiBerry input device
        device_index = find_hifiberry_input_device(pa)
        
        if device_index is None:
            print("✗ HiFiBerry input device not found in PyAudio devices")
            print()
            print("Available input devices:")
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    print(f"  {i}: {info['name']}")
            pa.terminate()
            return False
        
        print()
        print("Opening audio input stream...")
        
        # Open input stream
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        print("✓ Stream opened successfully")
        print()
        print(f"Recording for {duration} seconds...")
        print("(Speak into the microphone or make some noise)")
        print()
        
        # Record audio
        frames = []
        num_samples = int(sample_rate * duration)
        samples_read = 0
        
        start_time = time.time()
        
        while samples_read < num_samples:
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)
            samples_read += 1024
            
            # Show progress
            elapsed = time.time() - start_time
            if int(elapsed) != int(elapsed - 0.1):
                progress = min(100, (samples_read / num_samples) * 100)
                print(f"  Recording... {progress:.0f}%", end='\r')
        
        stream.stop_stream()
        stream.close()
        elapsed = time.time() - start_time
        
        print()
        print(f"✓ Recording complete ({elapsed:.2f} seconds)")
        print()
        
        # Convert to numpy array
        audio_data = b''.join(frames)
        samples = np.frombuffer(audio_data, dtype=np.int16)
        
        # Analyze audio
        print("Analyzing recorded audio...")
        max_amplitude = np.max(np.abs(samples))
        rms = np.sqrt(np.mean(samples.astype(np.float32) ** 2))
        peak_db = 20 * np.log10(max_amplitude / 32767.0) if max_amplitude > 0 else -np.inf
        rms_db = 20 * np.log10(rms / 32767.0) if rms > 0 else -np.inf
        
        print(f"  Samples recorded: {len(samples)}")
        print(f"  Max amplitude: {max_amplitude} ({peak_db:.1f} dB)")
        print(f"  RMS level: {rms:.1f} ({rms_db:.1f} dB)")
        print()
        
        # Check if audio was detected
        if max_amplitude < 100:
            print("⚠ Warning: Very low signal level detected")
            print("  - Check microphone connection")
            print("  - Check microphone is powered (if needed)")
            print("  - Speak louder or check input gain")
        elif max_amplitude > 30000:
            print("⚠ Warning: Very high signal level detected (possible clipping)")
            print("  - Reduce input gain")
        else:
            print("✓ Audio levels look good")
        
        print()
        
        # Optionally play back
        print("Would you like to play back the recording? (y/n): ", end='')
        # For automated testing, skip playback prompt
        play_back = False
        
        if play_back:
            print("Playing back recording...")
            output_device = None
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if 'hifiberry' in info['name'].lower() and info['maxOutputChannels'] > 0:
                    output_device = i
                    break
            
            if output_device is not None:
                out_stream = pa.open(
                    format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    output=True,
                    output_device_index=output_device,
                    frames_per_buffer=1024
                )
                
                out_stream.write(audio_data)
                out_stream.stop_stream()
                out_stream.close()
                print("✓ Playback complete")
            else:
                print("⚠ Could not find output device for playback")
        
        pa.terminate()
        
        print()
        print("=" * 60)
        print("✓ Audio input test complete")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def monitor_audio_levels(duration=10, sample_rate=44100):
    """Monitor audio input levels in real-time."""
    
    print("=" * 60)
    print("HiFiBerry Audio Input Level Monitor")
    print("=" * 60)
    print()
    print(f"Monitoring for {duration} seconds...")
    print("(Speak into microphone - levels will be displayed)")
    print("Press Ctrl+C to stop early")
    print()
    
    try:
        pa = pyaudio.PyAudio()
        
        device_index = find_hifiberry_input_device(pa)
        if device_index is None:
            print("✗ HiFiBerry input device not found")
            pa.terminate()
            return False
        
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        start_time = time.time()
        max_level = 0
        
        try:
            while time.time() - start_time < duration:
                data = stream.read(1024, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.int16)
                
                # Calculate level
                rms = np.sqrt(np.mean(samples.astype(np.float32) ** 2))
                peak = np.max(np.abs(samples))
                rms_db = 20 * np.log10(rms / 32767.0) if rms > 0 else -60
                peak_db = 20 * np.log10(peak / 32767.0) if peak > 0 else -60
                
                max_level = max(max_level, peak)
                
                # Visual level meter
                bar_length = int((rms / 32767.0) * 50)
                bar = '█' * bar_length + '░' * (50 - bar_length)
                
                print(f"RMS: {rms_db:6.1f} dB | Peak: {peak_db:6.1f} dB | [{bar}]", end='\r')
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print()
            print("Stopped by user")
        
        stream.stop_stream()
        stream.close()
        pa.terminate()
        
        print()
        print(f"✓ Monitoring complete - Max level: {max_level} ({20*np.log10(max_level/32767.0):.1f} dB)")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test HiFiBerry audio input')
    parser.add_argument('-d', '--duration', type=float, default=3.0,
                        help='Recording duration in seconds (default: 3.0)')
    parser.add_argument('-r', '--sample-rate', type=int, default=44100,
                        help='Sample rate in Hz (default: 44100)')
    parser.add_argument('-c', '--channels', type=int, default=1,
                        help='Number of channels (default: 1)')
    parser.add_argument('-m', '--monitor', action='store_true',
                        help='Monitor audio levels in real-time')
    parser.add_argument('--monitor-duration', type=float, default=10.0,
                        help='Monitor duration in seconds (default: 10.0)')
    
    args = parser.parse_args()
    
    if args.monitor:
        success = monitor_audio_levels(args.monitor_duration, args.sample_rate)
    else:
        success = test_audio_input(args.duration, args.sample_rate, args.channels)
    
    sys.exit(0 if success else 1)

