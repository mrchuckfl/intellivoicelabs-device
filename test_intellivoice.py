#!/usr/bin/env python3
"""Test script for IntelliVoice device configuration."""
import json
import sys

def test_config_load():
    """Test configuration loading."""
    try:
        with open("config.json") as f:
            config = json.load(f)
        print("✓ Config loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Config load failed: {e}")
        return False

def test_imports():
    """Test Python module imports."""
    modules = [
        "numpy",
        "pyaudio", 
        "luma.oled",
        "gpiozero",
        "onnxruntime",
        "PIL"
    ]
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            all_ok = False
    return all_ok

def test_audio_devices():
    """Test audio device availability."""
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        print("\nAvailable audio devices:")
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            print(f"  {i}: {info['name']}")
        pa.terminate()
        print("✓ Audio devices detected")
        return True
    except Exception as e:
        print(f"✗ Audio device test failed: {e}")
        return False

def test_i2c_devices():
    """Test I²C device availability."""
    try:
        import glob
        i2c_devices = glob.glob("/dev/i2c*")
        if i2c_devices:
            print("\nI²C devices available:")
            for dev in i2c_devices:
                print(f"  {dev}")
            return True
        else:
            print("✗ No I²C devices found")
            return False
    except Exception as e:
        print(f"✗ I²C test failed: {e}")
        return False

def test_gpio_access():
    """Test GPIO access."""
    try:
        from gpiozero import LED
        print("✓ GPIO access available")
        return True
    except Exception as e:
        print(f"✗ GPIO access failed: {e}")
        return False

def main():
    print("IntelliVoice Configuration Test")
    print("=" * 40)
    
    results = []
    
    print("\n1. Testing configuration...")
    results.append(test_config_load())
    
    print("\n2. Testing Python imports...")
    results.append(test_imports())
    
    print("\n3. Testing audio devices...")
    results.append(test_audio_devices())
    
    print("\n4. Testing I²C devices...")
    results.append(test_i2c_devices())
    
    print("\n5. Testing GPIO access...")
    results.append(test_gpio_access())
    
    print("\n" + "=" * 40)
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

