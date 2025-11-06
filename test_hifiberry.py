#!/usr/bin/env python3
"""Test script for HiFiBerry DAC+ADC Pro audio board."""
import subprocess
import sys

def test_hifiberry_detection():
    """Test if HiFiBerry is detected as ALSA device."""
    
    print("=" * 60)
    print("HiFiBerry DAC+ADC Pro Detection Test")
    print("=" * 60)
    print()
    
    try:
        # Check for playback device
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        output = result.stdout
        
        if 'hifiberry' in output.lower() or 'sndrpihifiberry' in output.lower():
            print("✓ HiFiBerry detected in playback devices:")
            for line in output.split('\n'):
                if 'hifiberry' in line.lower() or 'sndrpihifiberry' in line.lower():
                    print(f"  {line.strip()}")
            print()
        else:
            print("✗ HiFiBerry not found in playback devices")
            return False
        
        # Check for capture device
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        output = result.stdout
        
        if 'hifiberry' in output.lower() or 'sndrpihifiberry' in output.lower():
            print("✓ HiFiBerry detected in capture devices:")
            for line in output.split('\n'):
                if 'hifiberry' in line.lower() or 'sndrpihifiberry' in line.lower():
                    print(f"  {line.strip()}")
            print()
        else:
            print("✗ HiFiBerry not found in capture devices")
            return False
        
        # Get card number
        card_num = None
        for line in output.split('\n'):
            if 'hifiberry' in line.lower() or 'sndrpihifiberry' in line.lower():
                # Extract card number (format: "card X:")
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'card' and i + 1 < len(parts):
                        card_num = parts[i + 1].rstrip(':')
                        break
                break
        
        if card_num:
            print(f"✓ HiFiBerry card number: {card_num}")
            print()
            return True, card_num
        else:
            print("⚠ Could not determine card number")
            return True, None
            
    except Exception as e:
        print(f"✗ Error checking devices: {e}")
        return False, None

def test_audio_info(card_num):
    """Get detailed audio information."""
    
    print("=" * 60)
    print("HiFiBerry Audio Information")
    print("=" * 60)
    print()
    
    if card_num:
        try:
            # Get card info
            result = subprocess.run(['cat', f'/proc/asound/card{card_num}/id'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Card ID: {result.stdout.strip()}")
            
            # Get supported formats
            result = subprocess.run(['cat', f'/proc/asound/card{card_num}/pcm0p/info'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("\nPlayback capabilities:")
                print(result.stdout)
            
            result = subprocess.run(['cat', f'/proc/asound/card{card_num}/pcm0c/info'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("Capture capabilities:")
                print(result.stdout)
                
        except Exception as e:
            print(f"⚠ Could not get detailed info: {e}")

if __name__ == "__main__":
    success, card_num = test_hifiberry_detection()
    
    if success:
        if card_num:
            test_audio_info(card_num)
        print()
        print("=" * 60)
        print("✓ HiFiBerry board is detected and responding!")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("✗ HiFiBerry board not detected")
        print("=" * 60)
        sys.exit(1)

