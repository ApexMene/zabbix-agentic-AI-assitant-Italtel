"""FastAPI application for Network Troubleshooting Assistant."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from config import config
from services import MCPClient, alarm_aggregator, AlarmPoller, InstanceMonitor
from models import check_connection
from api.dependencies import set_mcp_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
alarm_poller = None
instance_monitor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global alarm_poller, instance_monitor
    
    # Startup
    logger.info("Starting application...")
    
    # Check database connection
    if not check_connection():
        logger.error("Database connection failed!")
        raise RuntimeError("Database not available")
    
    # Initialize MCP client
    mcp_url = config.mcp_server_url
    mcp_client = MCPClient(mcp_url)
    set_mcp_client(mcp_client)
    logger.info(f"MCP client initialized: {mcp_url}")
    
    # Initialize and start alarm poller
    poll_interval = config.polling_interval
    alarm_poller = AlarmPoller(mcp_client, alarm_aggregator, poll_interval)
    await alarm_poller.start()
    logger.info(f"Alarm poller started (interval: {poll_interval}s)")
    
    # Initialize and start instance monitor
    instance_monitor = InstanceMonitor(mcp_client, alarm_aggregator, poll_interval)
    await instance_monitor.start()
    logger.info("Instance monitor started")
    
    # Do initial poll
    await alarm_poller.poll_all_instances()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if alarm_poller:
        await alarm_poller.stop()
    if instance_monitor:
        await instance_monitor.stop()
    if mcp_client:
        await mcp_client.close()

# Create FastAPI app
app = FastAPI(
    title="Network Troubleshooting Assistant API",
    description="Backend API for AI-powered network troubleshooting",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:13000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from api.routes import instances, alarms, health

# Register routes
app.include_router(health.router, tags=["health"])
app.include_router(instances.router, prefix="/api/instances", tags=["instances"])
app.include_router(alarms.router, prefix="/api/alarms", tags=["alarms"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Network Troubleshooting Assistant API",
        "version": "1.0.0",
        "status": "operational"
    }
