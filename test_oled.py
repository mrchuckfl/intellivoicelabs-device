#!/usr/bin/env python3
"""Test script for OLED display (SSD1306)."""
import time
import sys

try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"Error: Missing required module: {e}")
    print("Please install: pip3 install luma.oled pillow")
    sys.exit(1)

def test_oled_display(port=13, address=0x3C):
    """Test OLED display with various patterns."""
    
    print("Initializing OLED display...")
    print(f"I²C Port: {port}")
    print(f"I²C Address: 0x{address:02X} ({address})")
    
    try:
        # Initialize display
        serial = i2c(port=port, address=address)
        device = ssd1306(serial, width=128, height=64)
        
        print("✓ OLED display initialized successfully!")
        print("")
        
        # Test 1: Clear screen (black)
        print("Test 1: Clearing screen...")
        image = Image.new("1", (device.width, device.height))
        device.display(image)
        time.sleep(1)
        
        # Test 2: Fill screen (white)
        print("Test 2: Filling screen white...")
        image = Image.new("1", (device.width, device.height), 255)
        device.display(image)
        time.sleep(1)
        
        # Test 3: Display text
        print("Test 3: Displaying text...")
        image = Image.new("1", (device.width, device.height))
        draw = ImageDraw.Draw(image)
        
        # Try to load a nice font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 14)
            except:
                font = ImageFont.load_default()
        
        # Draw multiple lines of text
        lines = [
            "IntelliVoice",
            "OLED Test",
            "I2C: OK",
            "Display: OK"
        ]
        
        y_offset = 0
        for line in lines:
            draw.text((0, y_offset), line, fill=255, font=font)
            y_offset += 16
        
        device.display(image)
        time.sleep(3)
        
        # Test 4: Draw diagonal lines
        print("Test 4: Drawing diagonal lines...")
        image = Image.new("1", (device.width, device.height))
        draw = ImageDraw.Draw(image)
        
        # Draw some lines
        for i in range(0, 128, 16):
            draw.line([(0, 0), (i, 64)], fill=255)
        
        device.display(image)
        time.sleep(2)
        
        # Test 5: Draw rectangles
        print("Test 5: Drawing rectangles...")
        image = Image.new("1", (device.width, device.height))
        draw = ImageDraw.Draw(image)
        
        draw.rectangle([10, 10, 60, 30], outline=255)
        draw.rectangle([70, 10, 120, 30], fill=255)
        draw.rectangle([10, 40, 60, 60], fill=255)
        draw.rectangle([70, 40, 120, 60], outline=255)
        
        device.display(image)
        time.sleep(2)
        
        # Test 6: Final message
        print("Test 6: Displaying final message...")
        image = Image.new("1", (device.width, device.height))
        draw = ImageDraw.Draw(image)
        
        final_message = "OLED Test\nComplete!"
        draw.text((20, 20), final_message, fill=255, font=font)
        device.display(image)
        time.sleep(2)
        
        # Clear screen
        image = Image.new("1", (device.width, device.height))
        device.display(image)
        
        print("")
        print("✓ All OLED tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing OLED display: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Try default configuration
    import json
    try:
        with open("config.json") as f:
            config = json.load(f)
            port = config["display"].get("i2c_port", 13)
            address = config["display"].get("i2c_address", 60)
    except:
        port = 13
        address = 0x3C
    
    print("=" * 60)
    print("IntelliVoice OLED Display Test")
    print("=" * 60)
    print()
    
    success = test_oled_display(port, address)
    
    print()
    print("=" * 60)
    if success:
        print("✓ OLED display test PASSED")
        sys.exit(0)
    else:
        print("✗ OLED display test FAILED")
        sys.exit(1)

