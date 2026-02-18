from http.server import BaseHTTPRequestHandler
import json
import os
import requests

# Configurações
DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = self.path
        
        # Status do bot
        if path == '/api/status':
            result = self.get_status()
        
        # Comando GDP
        elif path.startswith('/api/gdp/'):
            parts = path.split('/')
            if len(parts) >= 4:
                server_id = parts[3]
                quantidade = parts[4] if len(parts) >= 5 else '100'
                result = self.send_command(f"!gdp {quantidade} {server_id}")
            else:
                result = {"erro": "URL inválida"}
        
        # Comando Nuclear
        elif path.startswith('/api/nuclear/'):
            parts = path.split('/')
            if len(parts) >= 4:
                server_id = parts[3]
                result = self.send_command(f"!nuclear {server_id}")
            else:
                result = {"erro": "URL inválida"}
        
        else:
            result = {
                "status": "online",
                "comandos": [
                    "/api/status",
                    "/api/gdp/ID_SERVIDOR/QUANTIDADE",
                    "/api/nuclear/ID_SERVIDOR"
                ]
            }
        
        self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def get_status(self):
        """Verifica status do bot na Discloud"""
        if not DISCLOUD_TOKEN:
            return {"status": "offline", "erro": "Token não configurado"}
        
        try:
            headers = {'api-token': DISCLOUD_TOKEN}
            response = requests.get(
                f"https://discloud.com/api/rest/app/{BOT_ID}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "online",
                    "servidores": data.get('guilds', 0),
                    "nome": data.get('name', 'Zxy-panda')
                }
            else:
                return {"status": "offline"}
        except:
            return {"status": "offline"}
    
    def send_command(self, comando):
        """Envia comando para o bot"""
        if not DISCLOUD_TOKEN:
            return {"erro": "Token não configurado"}
        
        try:
            headers = {
                'api-token': DISCLOUD_TOKEN,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"https://discloud.com/api/rest/app/{BOT_ID}/cmd",
                headers=headers,
                json={"command": comando},
                timeout=10
            )
            
            if response.status_code == 200:
                return {"sucesso": True, "comando": comando}
            else:
                return {"erro": f"Erro {response.status_code}"}
        except Exception as e:
            return {"erro": str(e)}