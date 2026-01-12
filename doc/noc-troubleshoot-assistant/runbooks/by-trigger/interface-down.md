# Interface Down - Network Link Failure

## Problem Description
Network interface on router or switch has gone down, indicating physical or logical link failure.

## Severity
**High to Disaster** - Depending on interface criticality and redundancy

## Common Root Causes
1. **Physical Layer** - Cable unplugged, fiber cut, transceiver failure
2. **Link Protocol** - Keepalive timeout, protocol mismatch
3. **Configuration Error** - Interface shutdown, wrong encapsulation
4. **Hardware Failure** - NIC failure, port malfunction
5. **Upstream Issue** - Peer device down or interface down

## Diagnostic Steps

### 1. Check Interface Status
```bash
# FRRouting
vtysh -c "show interface <interface_name>"

# Look for:
# - Link status (up/down)
# - Protocol status
# - Last state change time
# - Error counters
```

### 2. Check Physical Layer
```bash
# Check link status
vtysh -c "show interface <interface_name>" | grep -i "link\|status"

# Check for errors
vtysh -c "show interface <interface_name>" | grep -i "error\|drop\|crc"
```

### 3. Check Peer Connectivity
```bash
# If IP configured, ping peer
ping <peer_ip>

# Check ARP
vtysh -c "show arp" | grep <interface_name>
```

### 4. Review Recent Changes
```bash
# Check syslog for interface events
grep <interface_name> /var/log/syslog | tail -50

# Check FRR logs
tail -100 /var/log/frr/frr.log | grep <interface_name>
```

## Resolution Steps

### If Interface Administratively Down
```bash
vtysh
configure terminal
interface <interface_name>
  no shutdown
exit
write memory
```

### If Physical Layer Issue
1. **Check cable connection** - Reseat cables
2. **Check transceiver** - Verify SFP/SFP+ is seated properly
3. **Test with different cable** - Rule out cable fault
4. **Check peer device** - Verify peer interface is up

### If Protocol Mismatch
```bash
vtysh
configure terminal
interface <interface_name>
  # Verify encapsulation matches peer
  show running-config interface <interface_name>
  
  # Common fixes:
  # encapsulation dot1q <vlan_id>
  # mtu 1500
exit
```

### If Error Counters High
```bash
# Clear counters and monitor
vtysh -c "clear interface <interface_name> counters"

# Wait 1 minute, check again
vtysh -c "show interface <interface_name>" | grep -i error

# If errors persist, likely hardware issue
```

## Impact Assessment
- **Core/Backbone Link**: Potential network partition, rerouting traffic
- **Access Link**: Single site/customer affected
- **Redundant Link**: Reduced redundancy, no immediate impact
- **Management Link**: Monitoring blind spot only

## Escalation Criteria
- Core or backbone interface down
- No redundant path available
- Multiple interfaces down on same device
- Customer-impacting outage
- Unable to restore within 15 minutes

## Escalation Path
1. **Senior Network Engineer** - For complex routing issues
2. **Field Technician** - For physical layer problems
3. **Network Architect** - For design changes needed
4. **Vendor TAC** - For hardware RMA

## Prevention
- Implement link redundancy (LACP, bonding)
- Regular cable plant inspection
- Spare transceiver inventory
- Automated failover testing
- Interface error rate monitoring
