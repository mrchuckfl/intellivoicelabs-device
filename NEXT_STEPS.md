# IntelliVoice Device - Next Steps Guide

## Current Status ✅

All software components are deployed and tested on the Raspberry Pi 5 server (mrchuck@192.168.1.53). The system is ready for hardware integration.

### What's Complete
- ✅ Software dependencies installed
- ✅ Project files deployed to server
- ✅ Configuration verified
- ✅ Test suite passing
- ✅ Code improved with error handling
- ✅ GitHub repository created and synced
- ✅ Systemd service file created

### What's Remaining
- ⏳ Physical hardware wiring
- ⏳ Hardware testing (GPIO, OLED, audio)
- ⏳ ONNX model integration
- ⏳ Final system testing

---

## Immediate Next Steps

### 1. Physical Hardware Setup

#### Required Hardware Connections

**Audio Path:**
- CB Microphone → NE5532 Preamp → ADS1256 ADC (SPI)
- DAC8532 DAC (SPI) → Amplifier/Speaker

**GPIO Connections:**
- GPIO17: Bypass button
- GPIO27: Language button
- GPIO22: LED ring #1 (Bypass mode indicator)
- GPIO23: LED ring #2 (Convert mode indicator)
- GPIO24: PTT input signal

**I²C:**
- GPIO2 (SDA) → OLED display
- GPIO3 (SCL) → OLED display

#### Wiring Checklist
```bash
# SSH to the device
ssh mrchuck@192.168.1.53

# Test I²C bus (should detect OLED at 0x3C)
sudo i2cdetect -y 13

# Test GPIO pins (will require actual hardware)
# Create simple test scripts for each component
```

---

### 2. Hardware Testing

Once hardware is connected, test each component:

#### Test OLED Display
```python
# Create test script: test_oled.py
import time
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

serial = i2c(port=13, address=0x3C)
device = ssd1306(serial, width=128, height=64)

# Test basic text rendering
image = Image.new("1", (128, 64))
draw = ImageDraw.Draw(image)
draw.text((0, 0), "OLED Test", fill=255)
device.display(image)
print("OLED test complete!")
```

#### Test GPIO Buttons
```python
# Create test: test_buttons.py
from gpiozero import Button, LED
import time

# Test buttons
btn_bypass = Button(17, pull_up=False)
btn_lang = Button(27, pull_up=False)

# Test LEDs
led1 = LED(22)
led2 = LED(23)

print("Testing buttons and LEDs...")
print("Press buttons to verify")
led1.blink()
led2.blink()
```

#### Test Audio (after ADS1256/DAC8532 configured)
```bash
# List audio devices
arecord -l
aplay -l

# Record test
arecord -D hw:0,0 -f S16_LE -r 16000 -c 1 test.wav

# Play back
aplay -D hw:0,0 test.wav
```

---

### 3. Audio Board Configuration

The ADS1256/DAC8532 board requires SPI configuration. You'll need to:

1. **Verify SPI connection:**
   ```bash
   ls -l /dev/spi*
   # Should show devices like /dev/spidev0.0, /dev/spidev1.0, etc.
   ```

2. **Create custom ALSA configuration** (if needed):
   - Edit `/etc/asound.conf` or `~/.asoundrc`
   - Map SPI devices to ALSA devices

3. **Test low-latency settings:**
   ```bash
   # Set CPU governor
   sudo cpufreq-set -g performance
   
   # Test with reduced buffer sizes
   # Edit config.json to test: 128, 256, 512, 1024 frames
   ```

---

### 4. ONNX Model Integration

#### Get/Prepare Voice Conversion Model

1. **Obtain model file:**
   - Place `voice_converter.onnx` in project directory
   - Ensure it's compatible with ONNX Runtime 1.21.0

2. **Update conversion function in main.py:**
   ```python
   def _convert_identity(self, data, session):
       if session is None:
           return data
       
       # Convert audio to model input format
       # Run model inference
       # Convert output back to audio
       
       return converted_audio
   ```

3. **Test model performance:**
   ```bash
   # Run application and monitor CPU usage
   python3 main.py
   
   # In another terminal:
   top
   # or
   htop
   ```

---

### 5. Install as System Service

Once hardware testing is complete:

```bash
# On the server
cd /home/mrchuck/Projects/intellivoice-device
sudo ./install_service.sh

# Start the service
sudo systemctl start intellivoice.service

# Check status
sudo systemctl status intellivoice.service

# View logs
sudo journalctl -u intellivoice.service -f
```

---

### 6. Final Testing

#### Integration Tests
```bash
# Run the application
python3 main.py

# Test mode switching (hardware button or simulated)
# Verify OLED display updates
# Check LED indicators
# Test audio path
```

#### Performance Tests
```bash
# Monitor system resources
htop

# Check for audio dropouts
cat /proc/asound/card*/pcm*/sub*/status

# Test extended operation
# Run for 1+ hour and monitor for stability issues
```

---

## Troubleshooting

### OLED Display Not Working
```bash
# Check I²C connection
sudo i2cdetect -y 13

# Verify address in config.json (should be 60 = 0x3C)

# Test with luma.oled directly
python3 test_oled.py
```

### GPIO Not Working
```bash
# Check permissions
groups
# Should include: gpio audio

# Test individual pins
# Use gpiozero directly in Python REPL
```

### Audio Issues
```bash
# Check ALSA configuration
aplay -l
arecord -l

# Check for buffer underruns
cat /proc/asound/card*/pcm*/sub*/status | grep -i underrun

# Adjust buffer sizes in config.json
```

### High Latency
```bash
# Set CPU governor to performance
sudo cpufreq-set -g performance

# Reduce buffer sizes in config.json
# Test: 128, 256, 512, 1024 frames

# Monitor latency measurement in OLED display
```

---

## Useful Commands

```bash
# SSH to device
ssh mrchuck@192.168.1.53

# Check I²C devices
sudo i2cdetect -y 13

# Check GPIO
gpio readall

# Check audio devices
arecord -l && aplay -l

# Run application
cd /home/mrchuck/Projects/intellivoice-device
python3 main.py

# Service management
sudo systemctl start intellivoice.service
sudo systemctl stop intellivoice.service
sudo systemctl status intellivoice.service
sudo journalctl -u intellivoice.service -f

# Run tests
python3 test_intellivoice.py
```

---

## Resources

- **GitHub Repository:** https://github.com/mrchuckfl/intellivoicelabs-device
- **Technical Spec:** IntelliVoice_Technical_Spec.txt
- **Deployment Status:** DEPLOYMENT_STATUS.md
- **Implementation Summary:** IMPLEMENTATION_SUMMARY.md

---

## Support

For issues or questions:
1. Check logs: `sudo journalctl -u intellivoice.service -f`
2. Review configuration: `config.json`
3. Run test suite: `python3 test_intellivoice.py`
4. Check hardware connections with multimeter

