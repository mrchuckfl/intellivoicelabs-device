# OLED Display Troubleshooting

## Expected Connections (SSD1306 OLED)

### Physical Connections
- **VCC** → 3.3V or 5V (check OLED spec)
- **GND** → Ground
- **SDA** → GPIO 2 (Physical pin 3)
- **SCL** → GPIO 3 (Physical pin 5)

### Address Selection
SSD1306 OLEDs typically use:
- **Address 0x3C** (most common, 60 decimal)
- **Address 0x3D** (if SA0 pin is pulled HIGH)

## Quick Diagnostic Steps

### 1. Verify Physical Wiring
```bash
# On the Pi, check GPIO pin states:
gpioinfo | grep -E 'gpio 2|gpio 3'

# Should show them available
```

### 2. Test I²C Communication
```bash
# Try reading directly from the OLED
sudo i2cget -y 13 0x3C 0x00

# If that fails, try address 0x3D
sudo i2cget -y 13 0x3D 0x00
```

### 3. Check Power
- Measure voltage at OLED VCC pin (should be 3.3V or 5V)
- Verify GND is connected to a known ground point

### 4. Verify I²C Pullups
SSD1306 requires 4.7kΩ pullups on SDA and SCL
- Most OLED modules have these built-in
- If using bare OLED chip, add pullups

### 5. Try Different I²C Bus
```bash
# Test all available buses
for bus in 13 14; do
    echo "Testing bus $bus..."
    sudo i2cdetect -y $bus
done
```

## Common Issues and Solutions

### Issue: "Remote I/O error"
**Cause:** OLED not powered or not connected  
**Solution:** Check power connections, verify continuity

### Issue: "I2C device not found"
**Cause:** Wrong I²C bus number or address  
**Solution:** Try different bus numbers (0, 1, 13, 14) and addresses (0x3C, 0x3D)

### Issue: No response at all
**Cause:** Wiring problem (crossed signals, loose connections)  
**Solution:** Double-check all connections with multimeter

## Test Scripts Available

1. **test_oled.py** - Full OLED test with visual patterns
2. **diagnose_i2c.sh** - I²C bus diagnostic
3. **Manual test** - Direct I²C read/write

## Next Steps

1. Double-check all 4 OLED connections physically
2. Measure voltage at OLED VCC pin
3. Try swapping SDA and SCL
4. Verify ground connection
5. If possible, test OLED on different Pi or different module

