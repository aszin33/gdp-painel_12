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
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        path = self.path
        print(f"📡 Requisição recebida: {path}")
        
        # Status do bot
        if path == '/api/status' or path == '/api/command/status':
            result = self.get_status()
        
        # Comando GDP
        elif '/api/gdp/' in path or '/api/command/gdp/' in path:
            # Extrair ID e quantidade da URL
            partes = path.split('/')
            try:
                # Procura o índice onde está 'gdp'
                idx = partes.index('gdp')
                if len(partes) > idx + 1:
                    server_id = partes[idx + 1]
                    quantidade = partes[idx + 2] if len(partes) > idx + 2 else '100'
                    result = self.send_command(f"!gdp {quantidade} {server_id}")
                else:
                    result = {"erro": "URL incompleta"}
            except:
                result = {"erro": "Formato inválido. Use: /api/gdp/ID/QUANTIDADE"}
        
        # Comando Nuclear
        elif '/api/nuclear/' in path or '/api/command/nuclear/' in path:
            partes = path.split('/')
            try:
                idx = partes.index('nuclear')
                if len(partes) > idx + 1:
                    server_id = partes[idx + 1]
                    result = self.send_command(f"!nuclear {server_id}")
                else:
                    result = {"erro": "URL incompleta"}
            except:
                result = {"erro": "Formato inválido. Use: /api/nuclear/ID"}
        
        # Rota raiz
        elif path == '/api' or path == '/api/':
            result = {
                "nome": "GDP Control",
                "status": "online",
                "comandos": [
                    "/api/status",
                    "/api/gdp/ID_DO_SERVIDOR/QUANTIDADE",
                    "/api/nuclear/ID_DO_SERVIDOR"
                ]
            }
        
        else:
            result = {"erro": "Rota não encontrada"}
        
        self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
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
                    "nome": data.get('name', 'GDP Bot'),
                    "ram": data.get('ram', '100MB')
                }
            else:
                return {"status": "offline", "codigo": response.status_code}
        except Exception as e:
            return {"status": "offline", "erro": str(e)}
    
    def send_command(self, comando):
        """Envia comando para o bot via Discloud"""
        if not DISCLOUD_TOKEN:
            return {"erro": "Token não configurado"}
        
        try:
            headers = {
                'api-token': DISCLOUD_TOKEN,
                'Content-Type': 'application/json'
            }
            
            print(f"📤 Enviando comando: {comando}")
            
            response = requests.post(
                f"https://discloud.com/api/rest/app/{BOT_ID}/cmd",
                headers=headers,
                json={"command": comando},
                timeout=15
            )
            
            if response.status_code == 200:
                return {
                    "sucesso": True,
                    "comando": comando,
                    "mensagem": "Comando enviado com sucesso"
                }
            else:
                return {
                    "erro": f"Erro {response.status_code}",
                    "detalhes": response.text
                }
        except Exception as e:
            return {"erro": str(e)}