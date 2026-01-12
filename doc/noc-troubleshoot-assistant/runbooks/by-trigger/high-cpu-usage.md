# High CPU Usage - Network Device

## Problem Description
Network device (router, switch, or network function) is experiencing high CPU utilization above threshold.

## Severity
**High** - Can impact network performance and packet processing

## Common Root Causes
1. **Traffic Spike** - Sudden increase in network traffic
2. **Routing Protocol Issues** - BGP/OSPF/ISIS convergence or flapping
3. **Control Plane Attack** - DDoS or malicious traffic
4. **Software Bug** - Memory leak or inefficient process
5. **Configuration Error** - Misconfigured QoS or ACLs

## Diagnostic Steps

### 1. Check Current CPU Usage
```bash
# For FRRouting
vtysh -c "show processes cpu"

# For Linux-based NFs
top -bn1 | head -20
```

### 2. Identify Top Processes
```bash
# FRRouting
vtysh -c "show thread cpu"

# Linux
ps aux --sort=-%cpu | head -10
```

### 3. Check Interface Statistics
```bash
# FRRouting
vtysh -c "show interface"
vtysh -c "show ip route summary"

# Check for errors
vtysh -c "show interface" | grep -i error
```

### 4. Review Recent Configuration Changes
```bash
# Check configuration history
vtysh -c "show running-config" > /tmp/current_config.txt
diff /tmp/last_known_good.txt /tmp/current_config.txt
```

## Resolution Steps

### Immediate Actions
1. **Identify the process** consuming CPU
2. **Check if it's expected** (e.g., route calculation during convergence)
3. **Monitor trend** - Is it increasing or stable?

### If Traffic-Related
```bash
# Check interface rates
vtysh -c "show interface" | grep -A5 "input rate\|output rate"

# Implement rate limiting if needed
vtysh
configure terminal
interface eth0
  rate-limit input 1000000
  rate-limit output 1000000
exit
```

### If Routing Protocol Issue
```bash
# Check BGP neighbors
vtysh -c "show ip bgp summary"

# Check for flapping
vtysh -c "show ip bgp neighbors" | grep -i "state\|flap"

# Stabilize if needed
vtysh
configure terminal
router bgp 65000
  neighbor 10.0.0.1 shutdown
  # Wait 30 seconds
  no neighbor 10.0.0.1 shutdown
exit
```

### If Software Issue
```bash
# Restart the affected process (last resort)
systemctl restart frr

# Or specific daemon
systemctl restart bgpd
```

## Escalation Criteria
- CPU > 90% for more than 10 minutes
- Network outage or packet loss detected
- Multiple devices affected simultaneously
- Unable to identify root cause within 15 minutes

## Escalation Path
1. **L2 Network Engineer** - For routing protocol issues
2. **Network Architect** - For design-related problems
3. **Vendor Support** - For suspected software bugs

## Prevention
- Implement CPU usage monitoring with trending
- Set up alerts for sustained high CPU (not just spikes)
- Regular configuration backups
- Capacity planning and traffic analysis
