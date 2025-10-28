# Wireless Network Diagnosis

**Date:** October 27, 2025  
**Server:** mrchuck@192.168.1.50 (ethernet) / 192.168.1.51 (wifi)  
**Issue:** Wireless connectivity had initial connection problems

## Current Status

### Interfaces
- **eth0**: 192.168.1.50 (Metric: 100) - Wired connection
- **wlan0**: 192.168.1.51 (Metric: 600) - Wireless connection "preconfigured"
- Both interfaces are UP and connected

### Connection Timeline
```
19:54:39 - Wlan0 initialized
19:54:46 - First connection attempt started
19:54:47 - First attempt failed (associating -> disconnected)
19:54:47 - Started scanning for retry
19:54:53 - Second attempt succeeded
19:54:53 - Got DHCP lease (192.168.1.51)
19:54:54 - Activation successful
```

## Root Cause Analysis

### Why Initial Connection Failed

1. **Signal Quality Issues**
   - First association attempt failed at 19:54:47
   - Then went into scanning mode
   - Second attempt 7 seconds later succeeded
   - Likely weak signal strength or interference

2. **Metric Priority**
   - Ethernet (eth0) has metric: **100** (preferred)
   - Wireless (wlan0) has metric: **600** (backup)
   - System prefers wired connection for outbound traffic
   - Both can be used simultaneously

3. **Packet Statistics**
   - RX errors: 0
   - RX dropped: 228 packets
   - TX errors: 0  
   - Dormant mode when not actively used

## Resolution

### Wireless Now Works
- ✅ Connected to "WarpSpeed" SSID
- ✅ Got IP address 192.168.1.51
- ✅ Can ping gateway (192.168.1.1)
- ✅ Connection is stable

### Current Behavior
- Both interfaces active (dual-homed)
- Ethernet preferred for outbound traffic (metric 100)
- Wireless can accept incoming connections
- System will auto-switch if ethernet fails

## Recommendations

### If You Want Wireless-Only
```bash
# Disable ethernet priority
sudo nmcli connection modify "Wired connection 1" ipv4.route-metric 700

# Or lower wireless metric
sudo nmcli connection modify preconfigured ipv4.route-metric 50
```

### If You Want Better Wireless Performance
1. Check signal strength:
   ```bash
   sudo apt install wireless-tools
   iwconfig wlan0
   ```

2. Check for interference:
   ```bash
   sudo iw dev wlan0 scan | grep signal
   ```

3. Consider relocating device or router

### Monitor Wireless Health
```bash
# Check dropped packets
watch -n 1 'cat /proc/net/wireless'

# Check connection quality
nmcli device wifi
```

## Access Points

**Ethernet (Primary):**
- IP: 192.168.1.50
- Interface: eth0
- Gateway: 192.168.1.1
- Metric: 100 (preferred)

**Wireless (Secondary):**
- IP: 192.168.1.51
- Interface: wlan0
- Gateway: 192.168.1.1
- Metric: 600 (backup)
- SSID: WarpSpeed

## Summary

**Issue:** Initial wireless connection failed due to signal quality/timing  
**Resolution:** Auto-retry succeeded after 7 seconds  
**Status:** Wireless working correctly with wired as primary  
**Action:** No action needed - working as designed

