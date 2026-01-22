"""
Browser MCP Server

This module implements the browser MCP server for interacting with web pages.
"""

import asyncio
import json
import sys
from typing import Dict, Any
from playwright.async_api import async_playwright
import tempfile
import os


class BrowserMCP:
    """MCP server for browser operations."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def initialize_browser(self):
        """Initialize the browser instance."""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

    async def cleanup(self):
        """Clean up browser resources."""
        if self.page:
            await self.page.close()
            self.page = None
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request."""
        method = request.get('method')

        try:
            if method == 'navigate_url':
                return await self.navigate_url(request.get('params', {}))
            elif method == 'click_element':
                return await self.click_element(request.get('params', {}))
            elif method == 'fill_form':
                return await self.fill_form(request.get('params', {}))
            elif method == 'scrape_data':
                return await self.scrape_data(request.get('params', {}))
            elif method == 'take_screenshot':
                return await self.take_screenshot(request.get('params', {}))
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

    async def navigate_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            url = params.get('url')
            if not url:
                return {'error': {'code': -32602, 'message': 'URL parameter required'}}

            await self.initialize_browser()

            # Navigate to the URL
            response = await self.page.goto(url)

            return {
                'result': {
                    'success': True,
                    'url': self.page.url,
                    'status': response.status if response else None
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Navigation failed: {str(e)}'}}

    async def click_element(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Click an element on the page."""
        try:
            selector = params.get('selector')
            if not selector:
                return {'error': {'code': -32602, 'message': 'Selector parameter required'}}

            await self.initialize_browser()

            # Click the element
            await self.page.click(selector)

            return {
                'result': {
                    'success': True,
                    'element_clicked': selector
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Click failed: {str(e)}'}}

    async def fill_form(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fill a form field."""
        try:
            selector = params.get('selector')
            value = params.get('value', '')

            if not selector:
                return {'error': {'code': -32602, 'message': 'Selector parameter required'}}

            await self.initialize_browser()

            # Fill the form field
            await self.page.fill(selector, value)

            return {
                'result': {
                    'success': True,
                    'field_filled': selector,
                    'value': value
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Fill form failed: {str(e)}'}}

    async def scrape_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape data from the current page."""
        try:
            selectors = params.get('selectors', {})

            await self.initialize_browser()

            # If no selectors provided, return the page content
            if not selectors:
                content = await self.page.content()
                return {
                    'result': {
                        'success': True,
                        'content': content
                    }
                }

            # Scrape data based on provided selectors
            scraped_data = {}
            for key, selector in selectors.items():
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        text_content = await element.text_content()
                        scraped_data[key] = text_content.strip()
                    else:
                        scraped_data[key] = None
                except Exception as e:
                    scraped_data[key] = f"Error scraping {key}: {str(e)}"

            return {
                'result': {
                    'success': True,
                    'data': scraped_data
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Scrape failed: {str(e)}'}}

    async def take_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        try:
            path = params.get('path')
            full_page = params.get('full_page', False)

            if not path:
                # Create a temporary file if no path provided
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                path = temp_file.name
                temp_file.close()

            await self.initialize_browser()

            # Take screenshot
            await self.page.screenshot(path=path, full_page=full_page)

            return {
                'result': {
                    'success': True,
                    'screenshot_path': path
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Screenshot failed: {str(e)}'}}


async def run_server():
    """Run the browser MCP server."""
    server = BrowserMCP()

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

    # Clean up when done
    await server.cleanup()


if __name__ == '__main__':
    asyncio.run(run_server())