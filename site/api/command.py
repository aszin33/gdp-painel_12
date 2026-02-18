from http.server import BaseHTTPRequestHandler
import json
import os
import requests

# Seus dados
DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyOTcwNzEyNTkzNzY0MjI5NjciLCJrZXkiOiJCUXlWM0FYOWc3byJ9.U0FJh5CKC4dc5g4hUOMeDwksON6W5NCQXF4X2DvnvHY')
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
        print(f"📡 Requisição: {path}")
        
        # Rota de teste sem autenticação
        if path == '/api/test':
            result = {
                "status": "ok",
                "mensagem": "API funcionando",
                "token_configurado": True,
                "bot_id": BOT_ID
            }
        
        # Rota de status com autenticação
        elif path == '/api/status':
            headers = {'api-token': DISCLOUD_TOKEN}
            
            try:
                # Fazer requisição com o token
                response = requests.get(
                    f"https://discloud.com/api/rest/app/{BOT_ID}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = {
                        "status": "online",
                        "servidores": data.get('guilds', 0),
                        "nome": data.get('name', 'Zxy-panda')
                    }
                else:
                    result = {
                        "status": "offline",
                        "codigo": response.status_code,
                        "mensagem": "Token inválido ou bot não encontrado"
                    }
            except Exception as e:
                result = {
                    "status": "offline",
                    "erro": str(e)
                }
        
        # Rota para testar o token manualmente
        elif path == '/api/test-token':
            headers = {'api-token': DISCLOUD_TOKEN}
            
            try:
                # Testar com endpoint do usuário
                response = requests.get(
                    "https://discloud.com/api/rest/user",
                    headers=headers,
                    timeout=10
                )
                
                result = {
                    "token_funciona": response.status_code == 200,
                    "status_code": response.status_code,
                    "resposta": response.json() if response.status_code == 200 else response.text
                }
            except Exception as e:
                result = {"erro": str(e)}
        
        else:
            result = {
                "rotas": [
                    "/api/test",
                    "/api/status",
                    "/api/test-token",
                    "/api/gdp/ID/QUANTIDADE",
                    "/api/nuclear/ID"
                ]
            }
        
        self.wfile.write(json.dumps(result, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()