# Zabbix Agent Not Available

## Problem Description
Zabbix agent on monitored host is not responding to polling requests from Zabbix server.

## Severity
**Average** - Monitoring blind spot, but host may still be operational

## Common Root Causes
1. **Agent Service Stopped** - zabbix-agent daemon not running
2. **Network Connectivity** - Firewall, routing, or network outage
3. **Agent Configuration** - Wrong Server IP or ListenPort
4. **Host Unreachable** - Host is down or network isolated
5. **Resource Exhaustion** - Host out of memory/CPU preventing agent response
6. **Port Conflict** - Another service using port 10050

## Diagnostic Steps

### 1. Verify Host Reachability
```bash
# From Zabbix server
ping <host_ip>

# Check if agent port is open
nc -zv <host_ip> 10050
telnet <host_ip> 10050
```

### 2. Check Agent Status on Host
```bash
# SSH to the host
ssh <host_ip>

# Check agent service
systemctl status zabbix-agent
# or
service zabbix-agent status

# Check if agent is listening
netstat -tlnp | grep 10050
# or
ss -tlnp | grep 10050
```

### 3. Review Agent Logs
```bash
# Check agent logs
tail -f /var/log/zabbix/zabbix_agentd.log

# Look for errors
grep -i error /var/log/zabbix/zabbix_agentd.log | tail -20
```

### 4. Verify Agent Configuration
```bash
# Check configuration
cat /etc/zabbix/zabbix_agentd.conf | grep -E "^Server|^ListenIP|^ListenPort"

# Expected output:
# Server=<zabbix_server_ip>
# ListenIP=0.0.0.0
# ListenPort=10050
```

### 5. Test Agent Manually
```bash
# From Zabbix server, test agent
zabbix_get -s <host_ip> -k agent.ping

# Should return: 1
```

## Resolution Steps

### If Agent Service is Stopped
```bash
# Start the agent
systemctl start zabbix-agent

# Enable auto-start
systemctl enable zabbix-agent

# Verify it's running
systemctl status zabbix-agent
```

### If Firewall Blocking
```bash
# Check firewall rules
iptables -L -n | grep 10050

# Allow Zabbix agent port
iptables -A INPUT -p tcp --dport 10050 -j ACCEPT

# For firewalld
firewall-cmd --permanent --add-port=10050/tcp
firewall-cmd --reload
```

### If Configuration Issue
```bash
# Edit configuration
vi /etc/zabbix/zabbix_agentd.conf

# Update Server parameter
Server=<correct_zabbix_server_ip>

# Restart agent
systemctl restart zabbix-agent
```

### If Host Resource Issue
```bash
# Check system resources
free -h
df -h
top -bn1

# If out of memory, identify and kill problematic processes
# Or restart the host if necessary
```

## Automated Remediation
```bash
#!/bin/bash
# Auto-restart agent if stopped

HOST_IP=$1

ssh $HOST_IP << 'EOF'
if ! systemctl is-active --quiet zabbix-agent; then
    echo "Agent is down, restarting..."
    systemctl start zabbix-agent
    sleep 2
    systemctl status zabbix-agent
else
    echo "Agent is running"
fi
EOF
```

## Escalation Criteria
- Host completely unreachable (ping fails)
- Agent restart doesn't resolve issue
- Multiple hosts affected (potential network issue)
- Critical production service impacted

## Escalation Path
1. **Network Operations** - For network connectivity issues
2. **System Administrator** - For host-level problems
3. **Zabbix Administrator** - For monitoring infrastructure issues

## Prevention
- Monitor agent availability with trending
- Set up redundant monitoring paths
- Implement agent auto-restart via systemd
- Regular agent version updates
- Document baseline agent configuration
