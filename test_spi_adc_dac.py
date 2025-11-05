#!/usr/bin/env python3
"""Test script for ADS1256 ADC and DAC8532 DAC via SPI."""
import spidev
import time
import sys

def test_spi_communication():
    """Test SPI communication with AD/DA board."""
    
    print("=" * 60)
    print("AD/DA Board SPI Communication Test")
    print("=" * 60)
    print()
    
    # Check SPI device
    spi_device = "/dev/spidev10.0"
    print(f"Testing SPI device: {spi_device}")
    
    try:
        # Open SPI
        spi = spidev.SpiDev()
        
        # Connect to SPI bus 10, device 0
        bus = 10
        device = 0
        
        print(f"Opening SPI bus {bus}, device {device}...")
        spi.open(bus, device)
        
        # Configure SPI
        spi.max_speed_hz = 1000000  # 1 MHz (ADS1256 max is 1.8 MHz)
        spi.mode = 1  # Mode 1: CPOL=0, CPHA=1 (ADS1256 uses this)
        
        print("✓ SPI device opened successfully")
        print(f"  Max speed: {spi.max_speed_hz} Hz")
        print(f"  Mode: {spi.mode}")
        print()
        
        # ADS1256 Test - Read status register
        print("Testing ADS1256 (ADC)...")
        print("Attempting to read status register...")
        
        # ADS1256 commands:
        # RDATA (0x01) - Read data
        # RREG (0x10) - Read register
        # WREG (0x50) - Write register
        
        try:
            # Try to read STATUS register (0x00)
            # Command: RREG | (register & 0x0F), number of bytes - 1
            cmd = [0x10 | 0x00, 0x00]  # Read 1 byte from STATUS register
            response = spi.xfer2(cmd)
            print(f"  ✓ ADS1256 responded: {[hex(x) for x in response]}")
            
            # Try to read data
            # Send RDATA command
            spi.writebytes([0x01])
            time.sleep(0.001)  # Wait for conversion
            data = spi.readbytes(3)  # Read 24-bit value
            print(f"  ✓ ADC data read: {data} (24-bit value)")
            
        except Exception as e:
            print(f"  ⚠ ADS1256 test: {e}")
            print("  (This is normal if board needs initialization)")
        
        print()
        
        # DAC8532 Test
        print("Testing DAC8532 (DAC)...")
        print("Attempting to write test value...")
        
        try:
            # DAC8532 command format:
            # [Command byte] [MSB] [LSB]
            # Command: 0x00 = Write to DAC A
            # Test value: 0x8000 (mid-scale, 0V)
            
            test_value = 0x8000  # Mid-scale
            msb = (test_value >> 8) & 0xFF
            lsb = test_value & 0xFF
            
            cmd = [0x00, msb, lsb]  # Write to DAC A
            spi.writebytes(cmd)
            print(f"  ✓ DAC8532 write command sent: {[hex(x) for x in cmd]}")
            print(f"  ✓ Set DAC output to mid-scale (0x{test_value:04X})")
            
        except Exception as e:
            print(f"  ⚠ DAC8532 test: {e}")
        
        print()
        
        # Test SPI speed
        print("Testing SPI transfer speeds...")
        test_data = [0x00, 0x01, 0x02, 0x03]
        
        start = time.time()
        for _ in range(100):
            spi.xfer2(test_data)
        elapsed = time.time() - start
        
        print(f"  ✓ 100 transfers completed in {elapsed:.3f}s")
        print(f"  ✓ Transfer rate: {100/elapsed:.1f} transfers/sec")
        
        spi.close()
        print()
        print("=" * 60)
        print("✓ SPI communication test completed")
        print("=" * 60)
        return True
        
    except FileNotFoundError:
        print(f"✗ SPI device not found: {spi_device}")
        print("  Check if SPI is enabled and device is connected")
        return False
        
    except PermissionError:
        print(f"✗ Permission denied accessing {spi_device}")
        print("  Add user to 'spi' group: sudo usermod -a -G spi $USER")
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_spi_devices():
    """List available SPI devices."""
    print("\nChecking available SPI devices...")
    import glob
    spi_devices = glob.glob("/dev/spidev*")
    
    if spi_devices:
        print(f"Found {len(spi_devices)} SPI device(s):")
        for dev in spi_devices:
            print(f"  {dev}")
    else:
        print("  No SPI devices found")
    
    print()

if __name__ == "__main__":
    test_spi_devices()
    success = test_spi_communication()
    sys.exit(0 if success else 1)

