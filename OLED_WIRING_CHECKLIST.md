# OLED Display Wiring Checklist

## Current Status
- **I²C buses available:** /dev/i2c-13 and /dev/i2c-14
- **OLED detected:** NO
- **Test commands failing with:** "Remote I/O error"

## Wiring Verification

### Required Connections for SSD1306 OLED

1. **Power Connections**
   ```
   VCC → 3.3V (Pin 1) or 5V (Pin 2)
   GND → Ground (Pin 6 or any GND pin)
   ```

2. **Data Connections**
   ```
   SDA → GPIO 2 (Physical Pin 3)
   SCL → GPIO 3 (Physical Pin 5)
   ```

### Physical Pin Layout on Raspberry Pi 5

```
         3.3V [1]  [2]  5V
        GPIO2 [3]  [4]  5V
        GPIO3 [5]  [6]  GND
         ...
```

## Diagnostic Tests to Run

### 1. Check Power
```bash
# With multimeter, check voltage at OLED VCC pin
# Should read 3.3V or 5V
```

### 2. Test I²C Communication
```bash
# Try scanning again
sudo i2cdetect -y 13
sudo i2cdetect -y 14

# Look for ANY device addresses (not the strange all-addresses scan)
```

### 3. Verify Wiring
```bash
# Check continuity with multimeter:
# - VCC to 3.3V/5V source
# - GND to ground
# - SDA to GPIO 2 (pin 3)
# - SCL to GPIO 3 (pin 5)
```

### 4. Try Different Address
Some OLED modules use 0x3D instead of 0x3C:
```bash
sudo i2cget -y 13 0x3D 0x00
```

## Common Issues

### Issue: No Device Detected
**Possible causes:**
- Not powered (check VCC/GND)
- Wrong pins (verify GPIO 2/3)
- OLED module defective
- SDA/SCL wires swapped

### Issue: Remote I/O Error
**Possible causes:**
- OLED not powered
- Connections loose
- Wrong I²C bus
- OLED module fault

### Issue: All Addresses Show in Scan
**Possible causes:**
- Virtual I²C bus (not hardware)
- Pullup resistor issues
- Bus configuration problem

## Next Steps

1. **Verify physical connections physically**
   - Double-check each wire is in the correct pin
   - Ensure connections are secure and not loose
   
2. **Measure voltages**
   - Confirm OLED has power at VCC pin
   - Verify ground connection
   
3. **Try swapping SDA/SCL**
   - Some OLED modules have them labeled backwards
   - Swap the two wires and test again
   
4. **Check OLED module**
   - Verify the OLED is SSD1306 compatible
   - Check if it needs any jumpers or configuration

## Contact Information

If OLED still doesn't work after checking all connections:
- Share OLED module part number
- Check if it requires any specific initialization
- Verify it's designed for Raspberry Pi

