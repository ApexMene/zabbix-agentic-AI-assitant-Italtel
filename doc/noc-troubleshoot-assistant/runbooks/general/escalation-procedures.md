# Network Operations Center - Escalation Procedures

## Escalation Levels

### Level 1: NOC Engineer (You)
- **Response Time**: Immediate
- **Scope**: Initial investigation, standard troubleshooting
- **Authority**: Acknowledge alarms, restart services, basic configuration changes
- **Duration**: Up to 30 minutes

### Level 2: Senior Network Engineer
- **Response Time**: 15 minutes
- **Scope**: Complex troubleshooting, routing protocol issues, multi-device problems
- **Authority**: Major configuration changes, failover decisions
- **Contact**: On-call rotation (see oncall schedule)

### Level 3: Network Architect
- **Response Time**: 30 minutes (business hours), 1 hour (after hours)
- **Scope**: Design issues, capacity problems, architectural decisions
- **Authority**: Network design changes, vendor engagement
- **Contact**: architecture-team@company.com

### Level 4: Vendor TAC
- **Response Time**: Per SLA (typically 1-4 hours)
- **Scope**: Hardware failures, software bugs, RMA requests
- **Authority**: Vendor-specific issues
- **Contact**: Via support portal

## When to Escalate

### Immediate Escalation (Level 2+)
- **Disaster severity** alarms
- **Customer-impacting outage**
- **Core network failure**
- **Security incident suspected**
- **Multiple simultaneous failures**

### Escalate After 30 Minutes (Level 2)
- Unable to identify root cause
- Standard remediation steps failed
- Problem is worsening
- Requires configuration changes beyond your authority

### Escalate After 1 Hour (Level 3)
- Recurring issue requiring design change
- Capacity-related problem
- Vendor engagement needed

## Escalation Process

### 1. Gather Information
Before escalating, collect:
- Alarm details and timeline
- Troubleshooting steps taken
- Current system state
- Impact assessment
- Relevant logs and outputs

### 2. Document in Investigation
- Use AI assistant to document findings
- Export investigation history
- Include all tool outputs

### 3. Contact Next Level
```
Subject: [SEVERITY] Brief Description - Site/Device

Body:
- Alarm: [Description]
- Started: [Time]
- Impact: [Customer/Service affected]
- Steps Taken: [Summary]
- Current Status: [State]
- Assistance Needed: [Specific ask]
```

### 4. Handoff
- Remain available for questions
- Provide access credentials if needed
- Continue monitoring
- Update ticket/investigation

## Emergency Contacts

### Network Operations Center
- **Phone**: +1-XXX-XXX-XXXX
- **Email**: noc@company.com
- **Slack**: #noc-alerts

### On-Call Engineers
- **Check**: oncall.company.com
- **Page**: Use PagerDuty/Opsgenie

### Management
- **NOC Manager**: manager@company.com
- **Director of Network Operations**: director@company.com

## After Escalation

### Your Responsibilities
- Monitor the situation
- Implement fixes as directed
- Update documentation
- Close investigation when resolved
- Conduct post-mortem if required

### Documentation
- Complete investigation notes
- Update runbooks if new procedure discovered
- Share lessons learned with team
