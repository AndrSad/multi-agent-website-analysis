#!/usr/bin/env python3
"""
Simple static file server for testing the web interface.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def start_static_server(port=8080):
    """Start a simple static file server."""
    
    # Change to the directory containing the HTML file
    os.chdir(Path(__file__).parent)
    
    # Create a custom handler that serves files from current directory
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers to allow requests to the API
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
            super().end_headers()
        
        def do_OPTIONS(self):
            # Handle preflight requests
            self.send_response(200)
            self.end_headers()
    
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            print(f"🌐 Статический сервер запущен на http://localhost:{port}")
            print(f"📁 Обслуживает файлы из: {os.getcwd()}")
            print(f"🔗 Откройте: http://localhost:{port}/web_interface.html")
            print("⏹️  Нажмите Ctrl+C для остановки")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{port}/web_interface.html')
                print("🚀 Браузер открыт автоматически")
            except:
                print("⚠️  Не удалось открыть браузер автоматически")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Порт {port} уже используется. Попробуйте другой порт:")
            print(f"   python static_server.py {port + 1}")
        else:
            print(f"❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Неверный номер порта. Используется порт 8080")
    
    start_static_server(port)
