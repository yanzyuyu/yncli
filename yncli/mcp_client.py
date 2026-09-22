import json
import subprocess
import threading
import uuid
from typing import Dict, Any, Optional

class MCPClient:
    def __init__(self, command: str, args: list[str]):
        self.command = command
        self.args = args
        self.process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._pending_requests: Dict[str, Dict[str, Any]] = {}
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self.process = subprocess.Popen(
            [self.command] + self.args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self._thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._thread.start()
        self.initialize()

    def _read_stdout(self):
        if not self.process or not self.process.stdout: return
        for line in self.process.stdout:
            try:
                msg = json.loads(line)
                if "id" in msg:
                    with self._lock:
                        if str(msg["id"]) in self._pending_requests:
                            self._pending_requests[str(msg["id"])]["response"] = msg
                            self._pending_requests[str(msg["id"])]["event"].set()
            except Exception:
                pass

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP server not running")
        
        req_id = str(uuid.uuid4())
        req = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method
        }
        if params:
            req["params"] = params
            
        event = threading.Event()
        with self._lock:
            self._pending_requests[req_id] = {"event": event, "response": None}
            
        self.process.stdin.write(json.dumps(req) + "\n")
        self.process.stdin.flush()
        
        event.wait(timeout=10.0)
        with self._lock:
            resp = self._pending_requests.pop(req_id, {}).get("response")
            
        if not resp:
            raise TimeoutError("MCP request timed out")
            
        if "error" in resp:
            raise RuntimeError(f"MCP error: {resp['error']}")
            
        return resp.get("result")

    def initialize(self):
        return self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "yncli", "version": "1.0.0"}
        })

    def tools_list(self):
        return self.send_request("tools/list")

    def tools_call(self, name: str, arguments: dict):
        return self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None

_global_mcp_client: Optional[MCPClient] = None

def start_mcp_server(command: str, args: list[str]) -> str:
    global _global_mcp_client
    try:
        if _global_mcp_client:
            _global_mcp_client.stop()
        _global_mcp_client = MCPClient(command, args)
        _global_mcp_client.start()
        return f"Successfully started MCP server: {command} {' '.join(args)}"
    except Exception as e:
        return f"Failed to start MCP server: {e}"

def list_mcp_resources() -> str:
    global _global_mcp_client
    if not _global_mcp_client:
        return "MCP server is not running."
    try:
        res = _global_mcp_client.tools_list()
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error listing MCP resources: {e}"

def call_mcp_tool(name: str, arguments: dict) -> str:
    global _global_mcp_client
    if not _global_mcp_client:
        return "MCP server is not running."
    try:
        res = _global_mcp_client.tools_call(name, arguments)
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error calling MCP tool '{name}': {e}"
