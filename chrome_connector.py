import json
import requests
import websocket
import logging
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)

class ChromeConnector:
    """Handles connection to Chrome browser via DevTools Protocol"""
    
    def __init__(self):
        self.debug_port = None
        self.ws = None
        self.current_tab = None
        self.message_id = 0
        self.is_connected_flag = False
        
    def connect(self, port: int = 9222) -> bool:
        """
        Connect to Chrome browser with remote debugging enabled
        Chrome should be started with: chrome --remote-debugging-port=9222
        """
        try:
            self.debug_port = port
            
            # Test connection by getting version info
            response = requests.get(f'http://localhost:{port}/json/version', timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                logger.info(f"Connected to Chrome {version_info.get('Browser', 'Unknown version')}")
                self.is_connected_flag = True
                return True
            else:
                logger.error(f"Failed to connect: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection failed: {str(e)}")
            logger.info("Make sure Chrome is running with --remote-debugging-port=9222")
            return False
    
    def get_tabs(self) -> List[Dict]:
        """Get list of open Chrome tabs"""
        try:
            if not self.is_connected_flag:
                return []
                
            response = requests.get(f'http://localhost:{self.debug_port}/json', timeout=5)
            if response.status_code == 200:
                tabs = response.json()
                # Filter only page tabs (not extensions, etc.)
                page_tabs = [
                    {
                        'id': tab['id'],
                        'title': tab['title'],
                        'url': tab['url'],
                        'type': tab.get('type', 'page')
                    }
                    for tab in tabs 
                    if tab.get('type') == 'page' and not tab['url'].startswith('chrome://')
                ]
                return page_tabs
            else:
                logger.error(f"Failed to get tabs: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting tabs: {str(e)}")
            return []
    
    def select_tab(self, tab_id: str) -> bool:
        """Select a specific tab for interaction"""
        try:
            if not self.is_connected_flag:
                return False
            
            # Close existing websocket connection if any
            if self.ws:
                self.ws.close()
            
            # Get tab info
            response = requests.get(f'http://localhost:{self.debug_port}/json', timeout=5)
            if response.status_code != 200:
                return False
            
            tabs = response.json()
            selected_tab = next((tab for tab in tabs if tab['id'] == tab_id), None)
            
            if not selected_tab:
                logger.error(f"Tab with ID {tab_id} not found")
                return False
            
            # Connect to the tab via WebSocket
            ws_url = selected_tab['webSocketDebuggerUrl']
            self.ws = websocket.create_connection(ws_url, timeout=10)
            self.current_tab = selected_tab
            
            # Enable necessary domains
            self._send_command('Runtime.enable')
            self._send_command('DOM.enable')
            
            logger.info(f"Selected tab: {selected_tab['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error selecting tab: {str(e)}")
            return False
    
    def get_page_info(self) -> Dict:
        """Get basic information about the current page"""
        try:
            if not self.current_tab:
                return {}
            
            return {
                'title': self.current_tab['title'],
                'url': self.current_tab['url'],
                'id': self.current_tab['id']
            }
            
        except Exception as e:
            logger.error(f"Error getting page info: {str(e)}")
            return {}
    
    def get_page_html(self) -> Optional[str]:
        """Get the HTML content of the current page"""
        try:
            if not self.ws or not self.current_tab:
                return None
            
            # Get the document root
            response = self._send_command('DOM.getDocument')
            if not response or 'result' not in response:
                return None
            
            root_node_id = response['result']['root']['nodeId']
            
            # Get the outer HTML
            response = self._send_command('DOM.getOuterHTML', {
                'nodeId': root_node_id
            })
            
            if response and 'result' in response:
                return response['result']['outerHTML']
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting page HTML: {str(e)}")
            return None
    
    def is_connected(self) -> bool:
        """Check if connected to Chrome"""
        return self.is_connected_flag and self.current_tab is not None
    
    def _send_command(self, method: str, params: Dict = None) -> Dict:
        """Send a command to Chrome DevTools Protocol"""
        try:
            if not self.ws:
                return {}
            
            self.message_id += 1
            message = {
                'id': self.message_id,
                'method': method
            }
            
            if params:
                message['params'] = params
            
            self.ws.send(json.dumps(message))
            
            # Wait for response
            response_text = self.ws.recv()
            response = json.loads(response_text)
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending command {method}: {str(e)}")
            return {}
    
    def disconnect(self):
        """Disconnect from Chrome"""
        try:
            if self.ws:
                self.ws.close()
                self.ws = None
            self.current_tab = None
            self.is_connected_flag = False
            logger.info("Disconnected from Chrome")
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
