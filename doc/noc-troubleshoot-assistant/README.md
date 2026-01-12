# Network Troubleshooting Chat Assistant

AI-powered network troubleshooting assistant for monitoring and investigating Zabbix alarms across multiple instances.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- AWS credentials (for Bedrock access)

### Setup

1. **Clone and configure:**
```bash
cd noc-troubleshoot-assistant
cp .env.example .env
# Edit .env with your credentials
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **Access applications:**
- **Frontend UI: http://localhost:13000** ⭐
  - If you see a white screen, do a hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Backend API: http://localhost:13001
- MCP Server: http://localhost:13002
- pgAdmin: http://localhost:13050 (admin@local.dev / admin)

### Development

**Backend tests:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r tests/requirements.txt
pytest tests/ -v
```

## Architecture

```
Frontend (React) → Backend (FastAPI) → MCP Server (Flask) → Zabbix Instances
                         ↓
                   PostgreSQL
                         ↓
                   Amazon Bedrock
```

## Configuration

- `config/app.yaml` - Application settings
- `config/instances.yaml` - Zabbix instance configurations
- `.env` - Environment variables and credentials

## Project Status

### Phase 1: Foundation ✅ COMPLETE
- [x] Infrastructure setup (Docker Compose)
- [x] Database schema and models
- [x] Configuration management
- [x] Unit tests (18/18 passed)

### Phase 2: MCP Server ✅ COMPLETE
- [x] Flask MCP server with 9 Zabbix tools
- [x] Connected to 2 Zabbix instances (22 hosts total)
- [x] HTTP API endpoints
- [x] Unit tests (25/25 passed)

### Phase 3: Backend Core ✅ COMPLETE
- [x] FastAPI application
- [x] Alarm aggregator and poller (30s interval)
- [x] Instance monitor
- [x] REST API endpoints
- [x] Unit tests (11/11 passed)

### Phase 4: Frontend ✅ COMPLETE
- [x] Carrier-grade SOC UI
- [x] React + TypeScript + Material-UI
- [x] Real-time alarm display
- [x] Instance monitoring cards
- [x] Professional dark theme

### Phase 5: AI Agent ✅ COMPLETE
- [x] Strands framework integration
- [x] Amazon Bedrock (Claude Haiku 4.5)
- [x] 5 MCP tools as Strands tools
- [x] Streaming investigations
- [x] End-to-end AI troubleshooting

### Phase 6: History & Runbooks ✅ COMPLETE
- [x] Investigation history API
- [x] Full-text search and filtering
- [x] Export functionality (JSON)
- [x] 3 operational runbooks created

## Features

### ✅ Operational
- Multi-instance Zabbix monitoring (Network Backbone + 5G Core)
- Real-time alarm aggregation and display
- AI-powered investigation with streaming responses
- One-click alarm acknowledgment
- Investigation history with 30 investigations stored
- Auto-refresh every 30 seconds
- Carrier-grade SOC interface

### 📊 Current System
- **2 Zabbix Instances**: Both connected (v7.0.21)
- **22 Monitored Hosts**: 12 FRRouting + 10 Open5GS
- **Active Alarms**: Real-time monitoring
- **AI Model**: Claude Haiku 4.5 (global inference profile)
- **Database**: 30+ investigations with full audit trail

## Documentation

- `doc/detailed_requirements.md` - Complete requirements
- `doc/functional_specification.md` - Functional behavior
- `doc/design_specification.md` - Technical design
- `doc/IMPLEMENTATION_TASKS.md` - Implementation task list
