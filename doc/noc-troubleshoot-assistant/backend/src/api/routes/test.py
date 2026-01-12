"""Simple test endpoint for investigation."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio

router = APIRouter()

@router.post("/test-stream")
async def test_stream():
    """Test streaming without any database."""
    
    async def generate():
        yield f"data: {json.dumps({'type': 'test', 'message': 'Stream working'})}\n\n"
        await asyncio.sleep(1)
        yield f"data: {json.dumps({'type': 'test', 'message': 'Second chunk'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
