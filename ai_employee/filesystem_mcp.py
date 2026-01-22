"""
Filesystem MCP Server

This module implements the filesystem MCP server for reading/writing vault files.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Union


class FilesystemMCP:
    """MCP server for filesystem operations."""

    def __init__(self):
        self.cwd = Path.cwd()

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request."""
        method = request.get('method')

        try:
            if method == 'read_file':
                return await self.read_file(request.get('params', {}))
            elif method == 'write_file':
                return await self.write_file(request.get('params', {}))
            elif method == 'list_directory':
                return await self.list_directory(request.get('params', {}))
            elif method == 'create_directory':
                return await self.create_directory(request.get('params', {}))
            else:
                return {
                    'error': {
                        'code': -32601,
                        'message': f'Method {method} not found'
                    }
                }
        except Exception as e:
            return {
                'error': {
                    'code': -32603,
                    'message': f'Internal error: {str(e)}'
                }
            }

    async def read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file from the filesystem."""
        filepath = params.get('path')
        if not filepath:
            return {'error': {'code': -32602, 'message': 'Path parameter required'}}

        try:
            path = Path(filepath)
            # Security: Prevent directory traversal
            if '..' in str(path):
                return {'error': {'code': -32602, 'message': 'Invalid path'}}

            content = path.read_text(encoding='utf-8')
            return {'result': {'content': content}}
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Failed to read file: {str(e)}'}}

    async def write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to a file."""
        filepath = params.get('path')
        content = params.get('content', '')

        if not filepath:
            return {'error': {'code': -32602, 'message': 'Path parameter required'}}

        try:
            path = Path(filepath)
            # Security: Prevent directory traversal
            if '..' in str(path):
                return {'error': {'code': -32602, 'message': 'Invalid path'}}

            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            path.write_text(content, encoding='utf-8')
            return {'result': {'success': True}}
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Failed to write file: {str(e)}'}}

    async def list_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List files in a directory."""
        dirpath = params.get('path', '.')

        try:
            path = Path(dirpath)
            # Security: Prevent directory traversal
            if '..' in str(path):
                return {'error': {'code': -32602, 'message': 'Invalid path'}}

            if not path.exists():
                return {'error': {'code': -32602, 'message': 'Directory does not exist'}}

            if not path.is_dir():
                return {'error': {'code': -32602, 'message': 'Path is not a directory'}}

            files = []
            for item in path.iterdir():
                files.append({
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else 0,
                    'modified': item.stat().st_mtime
                })

            return {'result': {'files': files}}
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Failed to list directory: {str(e)}'}}

    async def create_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a directory."""
        dirpath = params.get('path')
        if not dirpath:
            return {'error': {'code': -32602, 'message': 'Path parameter required'}}

        try:
            path = Path(dirpath)
            # Security: Prevent directory traversal
            if '..' in str(path):
                return {'error': {'code': -32602, 'message': 'Invalid path'}}

            path.mkdir(parents=True, exist_ok=True)
            return {'result': {'success': True}}
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Failed to create directory: {str(e)}'}}


async def run_server():
    """Run the filesystem MCP server."""
    server = FilesystemMCP()

    # Read from stdin and write responses to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = await server.handle_request(request)

            # Add the request ID to the response
            response['id'] = request.get('id')

            # Write response to stdout
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            error_response = {
                'id': None,
                'error': {
                    'code': -32700,
                    'message': 'Parse error'
                }
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                'id': None,
                'error': {
                    'code': -32603,
                    'message': f'Server error: {str(e)}'
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    asyncio.run(run_server())