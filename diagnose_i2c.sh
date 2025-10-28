#!/bin/bash
# I²C Hardware Diagnostic Script

echo "============================================"
echo "I²C Hardware Diagnostic"
echo "============================================"
echo ""

echo "1. Checking I²C devices..."
ls -l /dev/i2c* 2>/dev/null || echo "No I²C devices found"
echo ""

echo "2. Scanning I²C buses for devices..."
for bus in /dev/i2c-[0-9]*; do
    bus_num=$(echo $bus | grep -o '[0-9]\+')
    echo "Scanning bus $bus_num:"
    sudo i2cdetect -y $bus_num
    echo ""
done

echo "3. Checking I²C kernel modules..."
lsmod | grep i2c
echo ""

echo "4. Current user permissions..."
groups | grep -q i2c && echo "✓ User is in i2c group" || echo "✗ User NOT in i2c group"
echo ""

echo "5. Trying to detect OLED at standard address (0x3C)..."
for bus in 0 1 13 14; do
    if [ -e /dev/i2c-$bus ]; then
        echo "Checking bus $bus..."
        sudo i2cdetect -y $bus | grep -q "3c" && echo "  ✓ Found device at 0x3C on bus $bus" || echo "  ✗ No device at 0x3C on bus $bus"
    fi
done

echo ""
echo "============================================"
echo "Diagnostic complete"
echo "============================================"

