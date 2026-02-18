from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse
import time

# ==================== CONFIGURAÇÕES FIXAS ====================

# SEUS DADOS - JÁ CONFIGURADOS
DISCLOUD_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyOTcwNzEyNTkzNzY0MjI5NjciLCJrZXkiOiJCUXlWM0FYOWc3byJ9.U0FJh5CKC4dc5g4hUOMeDwksON6W5NCQXF4X2DvnvHY"
BOT_ID = "1386082293533249546"

# Headers padrão para API da Discloud
HEADERS = {
    'api-token': DISCLOUD_TOKEN,
    'Content-Type': 'application/json',
    'User-Agent': 'GDP-Control/1.0'
}

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Processa requisições GET"""
        
        # CORS headers para permitir acesso do site
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
        
        print(f"📡 Requisição recebida: {path}")
        
        # ========== ROTA RAIZ ==========
        if path == '/' or path == '/api' or path == '/api/':
            result = self.rota_raiz()
        
        # ========== ROTA DE TESTE ==========
        elif path == '/api/test':
            result = self.rota_teste()
        
        # ========== ROTA DE STATUS DO BOT ==========
        elif path == '/api/status':
            result = self.rota_status()
        
        # ========== ROTA PARA LISTAR SERVIDORES ==========
        elif path == '/api/servidores':
            result = self.rota_servidores()
        
        # ========== ROTA PARA INFO DO BOT ==========
        elif path == '/api/info':
            result = self.rota_info_bot()
        
        # ========== ROTA PARA ENVIAR COMANDO GDP ==========
        elif path.startswith('/api/gdp/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                quantidade = partes[4] if len(partes) >= 5 else '100'
                result = self.enviar_comando(f"!gdp {quantidade} {server_id}")
            else:
                result = {"erro": "URL inválida. Use: /api/gdp/ID_DO_SERVIDOR/QUANTIDADE"}
        
        # ========== ROTA PARA ENVIAR COMANDO NUCLEAR ==========
        elif path.startswith('/api/nuclear/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                result = self.enviar_comando(f"!nuclear {server_id}")
            else:
                result = {"erro": "URL inválida. Use: /api/nuclear/ID_DO_SERVIDOR"}
        
        # ========== ROTA PARA EXECUTAR COMANDO PERSONALIZADO ==========
        elif path.startswith('/api/comando/'):
            # /api/comando/!gdp%20100%201234
            import urllib.parse
            comando = urllib.parse.unquote(path.replace('/api/comando/', ''))
            result = self.enviar_comando(comando)
        
        # ========== ROTA NÃO ENCONTRADA ==========
        else:
            result = {
                "erro": "Rota não encontrada",
                "rotas_disponiveis": [
                    "/api",
                    "/api/test",
                    "/api/status",
                    "/api/info",
                    "/api/servidores",
                    "/api/gdp/ID/QUANTIDADE",
                    "/api/nuclear/ID",
                    "/api/comando/COMANDO"
                ]
            }
        
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
    
    def chamar_api_discloud(self, endpoint, metodo='GET', dados=None):
        """Função genérica para chamar a API da Discloud"""
        url = f"https://discloud.com/api/rest{endpoint}"
        
        try:
            if metodo == 'GET':
                response = requests.get(url, headers=HEADERS, timeout=15)
            else:
                response = requests.post(url, headers=HEADERS, json=dados, timeout=15)
            
            return {
                "sucesso": response.status_code == 200,
                "status": response.status_code,
                "dados": response.json() if response.status_code == 200 else None,
                "texto": response.text if response.status_code != 200 else None
            }
        except requests.exceptions.ConnectionError:
            return {"sucesso": False, "erro": "Erro de conexão com a Discloud"}
        except requests.exceptions.Timeout:
            return {"sucesso": False, "erro": "Timeout na conexão"}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def enviar_comando(self, comando):
        """Envia um comando para o bot via terminal da Discloud"""
        
        print(f"📤 Enviando comando: {comando}")
        
        # Primeiro, verificar se o bot está online
        status = self.chamar_api_discloud(f"/app/{BOT_ID}")
        
        if not status['sucesso']:
            return {
                "status": "erro",
                "mensagem": "Não foi possível conectar ao bot",
                "detalhes": status.get('erro', 'Bot offline')
            }
        
        # Enviar comando via terminal
        resultado = self.chamar_api_discloud(
            f"/app/{BOT_ID}/cmd",
            metodo='POST',
            dados={"command": comando}
        )
        
        if resultado['sucesso']:
            return {
                "status": "sucesso",
                "comando": comando,
                "mensagem": f"Comando enviado com sucesso para o bot"
            }
        else:
            return {
                "status": "erro",
                "comando": comando,
                "mensagem": "Erro ao enviar comando",
                "detalhes": resultado.get('erro', 'Desconhecido')
            }
    
    # ==================== ROTAS ====================
    
    def rota_raiz(self):
        """Rota inicial da API"""
        return {
            "nome": "GDP Control API",
            "versao": "2.0",
            "status": "online",
            "bot": {
                "id": BOT_ID,
                "token_configurado": bool(DISCLOUD_TOKEN)
            },
            "endpoints": {
                "teste": "/api/test",
                "status": "/api/status",
                "info": "/api/info",
                "servidores": "/api/servidores",
                "gdp": "/api/gdp/ID_DO_SERVIDOR/QUANTIDADE",
                "nuclear": "/api/nuclear/ID_DO_SERVIDOR",
                "comando": "/api/comando/COMANDO"
            }
        }
    
    def rota_teste(self):
        """Rota para testar se a API está funcionando"""
        return {
            "status": "online",
            "mensagem": "API funcionando corretamente",
            "timestamp": int(time.time()),
            "configuracoes": {
                "token": "configurado" if DISCLOUD_TOKEN else "não configurado",
                "token_preview": DISCLOUD_TOKEN[:20] + "..." if DISCLOUD_TOKEN else None,
                "bot_id": BOT_ID
            }
        }
    
    def rota_status(self):
        """Verifica status do bot na Discloud"""
        
        # Tentar diferentes endpoints para garantir
        endpoints = [
            f"/app/{BOT_ID}",
            f"/user",
            f"/apps"
        ]
        
        resultados = []
        for endpoint in endpoints:
            res = self.chamar_api_discloud(endpoint)
            resultados.append({
                "endpoint": endpoint,
                "status": res['status'] if 'status' in res else None,
                "sucesso": res['sucesso']
            })
            
            if res['sucesso']:
                # Se algum endpoint funcionou, usamos ele
                if endpoint == f"/app/{BOT_ID}":
                    dados = res['dados']
                    return {
                        "status": "online",
                        "nome": dados.get('name', 'GDP Bot'),
                        "servidores": dados.get('guilds', 0),
                        "ram": dados.get('ram', '100MB'),
                        "online_desde": dados.get('onlineSince', ''),
                        "detalhes": dados
                    }
                elif endpoint == "/user":
                    # Se o user funcionou mas o app não, o bot pode estar offline
                    return {
                        "status": "offline",
                        "mensagem": "Bot offline ou ID incorreto",
                        "usuario": res['dados']
                    }
        
        # Nenhum endpoint funcionou
        return {
            "status": "offline",
            "mensagem": "Não foi possível conectar à Discloud",
            "testes": resultados
        }
    
    def rota_info_bot(self):
        """Informações detalhadas do bot"""
        resultado = self.chamar_api_discloud(f"/app/{BOT_ID}")
        
        if resultado['sucesso']:
            dados = resultado['dados']
            return {
                "status": "online",
                "id": BOT_ID,
                "nome": dados.get('name', 'Desconhecido'),
                "linguagem": dados.get('lang', 'Python'),
                "ram": dados.get('ram', '100MB'),
                "servidores": dados.get('guilds', 0),
                "usuarios": dados.get('users', 0),
                "online_desde": dados.get('onlineSince', ''),
                "comandos_executados": dados.get('commands', 0),
                "dados_completos": dados
            }
        else:
            return {
                "status": "offline",
                "id": BOT_ID,
                "erro": resultado.get('erro', 'Bot offline')
            }
    
    def rota_servidores(self):
        """Lista os servidores onde o bot está"""
        resultado = self.chamar_api_discloud(f"/app/{BOT_ID}")
        
        if resultado['sucesso']:
            dados = resultado['dados']
            return {
                "status": "online",
                "total_servidores": dados.get('guilds', 0),
                "servidores": dados.get('guildsList', [])
            }
        else:
            return {
                "status": "offline",
                "mensagem": "Não foi possível listar servidores"
            }