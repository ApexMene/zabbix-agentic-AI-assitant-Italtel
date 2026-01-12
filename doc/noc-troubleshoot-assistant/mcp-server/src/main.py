"""Flask MCP Server for Zabbix integration."""
from flask import Flask, jsonify, request
import logging
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from zabbix_client import get_client_manager
from tool_registry import TOOL_HANDLERS, TOOL_DEFINITIONS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        client_manager = get_client_manager()
        status = client_manager.get_all_status()
        all_connected = all(s.get('status') == 'connected' for s in status)
        
        return jsonify({
            "status": "healthy" if all_connected else "degraded",
            "zabbix_instances": status
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/tools', methods=['GET'])
def list_tools():
    """List all available MCP tools."""
    return jsonify({
        "tools": TOOL_DEFINITIONS
    }), 200

@app.route('/tools/<tool_name>/invoke', methods=['POST'])
def invoke_tool(tool_name: str):
    """Invoke a specific MCP tool.
    
    Request body:
        {
            "instance_id": "zabbix-backbone",
            "params": {...}
        }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "Request body required"}), 400
        
        instance_id = data.get('instance_id')
        if not instance_id:
            return jsonify({"success": False, "error": "instance_id required"}), 400
        
        params = data.get('params', {})
        
        # Get tool handler
        if tool_name not in TOOL_HANDLERS:
            return jsonify({"success": False, "error": f"Tool not found: {tool_name}"}), 404
        
        # Get Zabbix client
        try:
            client_manager = get_client_manager()
            client = client_manager.get_client(instance_id)
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to connect to instance: {str(e)}"}), 500
        
        # Execute tool
        handler = TOOL_HANDLERS[tool_name]
        result = handler(client, **params)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Tool invocation failed: {tool_name} - {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/instances', methods=['GET'])
def list_instances():
    """List all configured Zabbix instances with status."""
    try:
        client_manager = get_client_manager()
        status = client_manager.get_all_status()
        return jsonify({
            "instances": status
        }), 200
    except Exception as e:
        logger.error(f"Failed to list instances: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/instances/<instance_id>/status', methods=['GET'])
def instance_status(instance_id: str):
    """Get status for specific instance."""
    try:
        client_manager = get_client_manager()
        status = client_manager.check_connection(instance_id)
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Failed to check instance status: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal error: {e}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 13002))
    logger.info(f"Starting MCP Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
