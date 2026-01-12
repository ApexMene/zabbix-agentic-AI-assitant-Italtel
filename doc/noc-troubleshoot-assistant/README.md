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
- Frontend: http://localhost:13000
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
- [x] Unit tests (13/13 passed)
- [x] Integration tests (5/5 passed)

### Phase 2: MCP Server ✅ COMPLETE
- [x] Flask MCP server application
- [x] Zabbix client manager
- [x] 9 Zabbix tools implemented (host, problem, trigger, item, template, maintenance, system)
- [x] HTTP API endpoints (/health, /tools, /instances, /tools/{name}/invoke)
- [x] Docker containerization
- [x] Unit tests (16/16 passed)
- [x] Integration tests (all endpoints verified)

### Phase 3: Backend Core (Next)
- [ ] FastAPI application structure
- [ ] Alarm aggregator service
- [ ] Instance monitor service
- [ ] REST API endpoints

## Documentation

- `doc/detailed_requirements.md` - Complete requirements
- `doc/functional_specification.md` - Functional behavior
- `doc/design_specification.md` - Technical design
- `doc/IMPLEMENTATION_TASKS.md` - Implementation task list
