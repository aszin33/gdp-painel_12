from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse
import time

# ==================== CONFIGURAÇÕES ====================

# Suas configurações (serão substituídas pelas variáveis de ambiente da Vercel)
DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', 'eyJhbGciOiJIUzI1NiJ9.eyJpZCI6IjEyOTcwNzEyNTkzNzY0MjI5NjciLCJrZXkiOiJlYmE0NDBiZTg2YWFhZTkzNmQzZDY5OTY1MmNmIn0.WlI-ncUm4U1a26lS4ZzveI21d-imC7KFw5MI77K2_Rc')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')

# Headers para API da Discloud
def get_headers():
    return {
        'api-token': DISCLOUD_TOKEN,
        'Content-Type': 'application/json',
        'User-Agent': 'GDP-Control/1.0'
    }

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Processa requisições GET"""
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
        
        # Parsear URL
        parsed = urlparse(self.path)
        path = parsed.path
        
        print(f"📡 Requisição: {path}")
        print(f"🔑 Token configurado: {'Sim' if DISCLOUD_TOKEN else 'Não'}")
        
        # ========== ROTA DE VERIFICAÇÃO DE TOKEN ==========
        if path == '/api/verificar-token' or path == '/api/verificar':
            result = self.verificar_token()
        
        # ========== ROTA DE DIAGNÓSTICO COMPLETO ==========
        elif path == '/api/diagnostico':
            result = self.diagnostico_completo()
        
        # ========== ROTA DE TESTE BÁSICO ==========
        elif path == '/api/test':
            result = self.rota_teste()
        
        # ========== ROTA DE STATUS DO BOT ==========
        elif path == '/api/status':
            # Primeiro verifica se o token é válido
            token_valido = self.verificar_token_simples()
            if not token_valido:
                result = {
                    "status": "offline",
                    "erro": "Token inválido",
                    "mensagem": "Use /api/verificar-token para diagnosticar"
                }
            else:
                result = self.status_bot()
        
        # ========== ROTA DE INFORMAÇÕES DO BOT ==========
        elif path == '/api/info':
            token_valido = self.verificar_token_simples()
            if not token_valido:
                result = {
                    "status": "offline",
                    "erro": "Token inválido"
                }
            else:
                result = self.info_bot()
        
        # ========== ROTA PARA LISTAR SERVIDORES ==========
        elif path == '/api/servidores':
            token_valido = self.verificar_token_simples()
            if not token_valido:
                result = {
                    "status": "erro",
                    "erro": "Token inválido"
                }
            else:
                result = self.listar_servidores()
        
        # ========== ROTA PARA ENVIAR COMANDO GDP ==========
        elif path.startswith('/api/gdp/'):
            token_valido = self.verificar_token_simples()
            if not token_valido:
                result = {"erro": "Token inválido"}
            else:
                partes = path.split('/')
                if len(partes) >= 4:
                    server_id = partes[3]
                    quantidade = partes[4] if len(partes) >= 5 else '100'
                    result = self.enviar_comando(f"!gdp {quantidade} {server_id}")
                else:
                    result = {"erro": "URL inválida. Use: /api/gdp/ID_DO_SERVIDOR/QUANTIDADE"}
        
        # ========== ROTA PARA ENVIAR COMANDO NUCLEAR ==========
        elif path.startswith('/api/nuclear/'):
            token_valido = self.verificar_token_simples()
            if not token_valido:
                result = {"erro": "Token inválido"}
            else:
                partes = path.split('/')
                if len(partes) >= 4:
                    server_id = partes[3]
                    result = self.enviar_comando(f"!nuclear {server_id}")
                else:
                    result = {"erro": "URL inválida. Use: /api/nuclear/ID_DO_SERVIDOR"}
        
        # ========== ROTA PRINCIPAL ==========
        elif path == '/' or path == '/api' or path == '/api/':
            result = self.rota_principal()
        
        # ========== ROTA NÃO ENCONTRADA ==========
        else:
            result = {
                "erro": "Rota não encontrada",
                "rotas_disponiveis": [
                    "/api",
                    "/api/test",
                    "/api/verificar-token",
                    "/api/diagnostico",
                    "/api/status",
                    "/api/info",
                    "/api/servidores",
                    "/api/gdp/ID/QUANTIDADE",
                    "/api/nuclear/ID"
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
    
    # ==================== FUNÇÕES DE VERIFICAÇÃO ====================
    
    def verificar_token_simples(self):
        """Verifica rapidamente se o token é válido"""
        if not DISCLOUD_TOKEN:
            return False
        
        try:
            response = requests.get(
                "https://discloud.com/api/rest/user",
                headers={'api-token': DISCLOUD_TOKEN},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def verificar_token(self):
        """Verificação detalhada do token"""
        
        if not DISCLOUD_TOKEN:
            return {
                "valido": False,
                "erro": "Token não configurado",
                "instrucao": "Configure a variável DISCLOUD_TOKEN na Vercel",
                "token_atual": None
            }
        
        try:
            # Testar endpoint do usuário
            response = requests.get(
                "https://discloud.com/api/rest/user",
                headers={'api-token': DISCLOUD_TOKEN},
                timeout=10
            )
            
            if response.status_code == 200:
                dados = response.json()
                return {
                    "valido": True,
                    "status": "✅ Token válido!",
                    "usuario": dados.get('user', {}).get('username', 'Desconhecido'),
                    "email": dados.get('user', {}).get('email', ''),
                    "plano": dados.get('plan', {}).get('name', 'Free'),
                    "token_preview": DISCLOUD_TOKEN[:30] + "..."
                }
            elif response.status_code == 401:
                return {
                    "valido": False,
                    "status": "❌ Token inválido",
                    "erro": "Token rejeitado pela Discloud (401)",
                    "instrucao": "Gere um novo token com o comando .api no Discord da Discloud",
                    "token_preview": DISCLOUD_TOKEN[:30] + "..."
                }
            else:
                return {
                    "valido": False,
                    "status": f"❌ Erro {response.status_code}",
                    "resposta": response.text[:200],
                    "token_preview": DISCLOUD_TOKEN[:30] + "..."
                }
        except requests.exceptions.ConnectionError:
            return {
                "valido": False,
                "erro": "Erro de conexão com a Discloud",
                "instrucao": "Verifique se a Discloud está online"
            }
        except Exception as e:
            return {
                "valido": False,
                "erro": str(e)
            }
    
    def diagnostico_completo(self):
        """Faz diagnóstico completo testando vários endpoints"""
        
        if not DISCLOUD_TOKEN:
            return {
                "token_configurado": False,
                "erro": "Token não configurado",
                "instrucao": "Configure a variável DISCLOUD_TOKEN na Vercel"
            }
        
        resultados = []
        
        # Endpoints para testar
        endpoints = [
            {"nome": "Usuário", "url": "/user", "importante": True},
            {"nome": "Apps do usuário", "url": "/apps", "importante": True},
            {"nome": "Bot específico", "url": f"/app/{BOT_ID}", "importante": True},
            {"nome": "Status da API", "url": "/status", "importante": False}
        ]
        
        for ep in endpoints:
            try:
                start = time.time()
                response = requests.get(
                    f"https://discloud.com/api/rest{ep['url']}",
                    headers={'api-token': DISCLOUD_TOKEN},
                    timeout=10
                )
                elapsed = time.time() - start
                
                info = {
                    "teste": ep['nome'],
                    "url": ep['url'],
                    "status": response.status_code,
                    "tempo": f"{elapsed:.2f}s",
                    "funcionou": response.status_code == 200
                }
                
                if response.status_code == 200:
                    try:
                        dados = response.json()
                        info["resumo"] = str(dados)[:100] + "..."
                    except:
                        info["resumo"] = response.text[:100]
                else:
                    info["erro"] = response.text[:100]
                
                resultados.append(info)
                
            except Exception as e:
                resultados.append({
                    "teste": ep['nome'],
                    "erro": str(e)
                })
        
        # Análise dos resultados
        token_valido = any(r.get('funcionou') for r in resultados if r.get('importante', False))
        
        if token_valido:
            conclusao = "✅ Token válido! Conexão estabelecida."
        else:
            conclusao = "❌ Token inválido ou sem acesso. Gere um novo token com .api"
        
        return {
            "token": {
                "configurado": True,
                "preview": DISCLOUD_TOKEN[:30] + "...",
                "tamanho": len(DISCLOUD_TOKEN)
            },
            "bot_id": BOT_ID,
            "resultados": resultados,
            "conclusao": conclusao,
            "proximos_passos": [
                "Se o token for inválido: vá no Discord da Discloud e digite .api",
                "Se o token for válido mas o bot não for encontrado: verifique o BOT_ID",
                "Se tudo funcionar: use /api/status para ver o bot"
            ]
        }
    
    # ==================== FUNÇÕES DO BOT ====================
    
    def rota_principal(self):
        """Rota principal da API"""
        token_valido = self.verificar_token_simples()
        
        return {
            "nome": "GDP Control API",
            "versao": "3.0",
            "status": "online",
            "token": {
                "configurado": bool(DISCLOUD_TOKEN),
                "valido": token_valido
            },
            "bot": {
                "id": BOT_ID
            },
            "endpoints": {
                "verificar_token": "/api/verificar-token",
                "diagnostico": "/api/diagnostico",
                "status": "/api/status",
                "info": "/api/info",
                "servidores": "/api/servidores",
                "gdp": "/api/gdp/ID/QUANTIDADE",
                "nuclear": "/api/nuclear/ID"
            }
        }
    
    def rota_teste(self):
        """Rota de teste básico"""
        return {
            "status": "online",
            "mensagem": "API funcionando",
            "timestamp": time.time(),
            "token_configurado": bool(DISCLOUD_TOKEN)
        }
    
    def status_bot(self):
        """Pega status do bot"""
        try:
            response = requests.get(
                f"https://discloud.com/api/rest/app/{BOT_ID}",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                dados = response.json()
                return {
                    "status": "online",
                    "nome": dados.get('name', 'Desconhecido'),
                    "servidores": dados.get('guilds', 0),
                    "ram": dados.get('ram', '100MB'),
                    "online_desde": dados.get('onlineSince', '')
                }
            elif response.status_code == 404:
                return {
                    "status": "offline",
                    "erro": "Bot não encontrado",
                    "codigo": 404,
                    "instrucao": "Verifique se o BOT_ID está correto"
                }
            else:
                return {
                    "status": "offline",
                    "codigo": response.status_code,
                    "resposta": response.text[:100]
                }
        except Exception as e:
            return {
                "status": "offline",
                "erro": str(e)
            }
    
    def info_bot(self):
        """Informações detalhadas do bot"""
        try:
            response = requests.get(
                f"https://discloud.com/api/rest/app/{BOT_ID}",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "online",
                    "dados": response.json()
                }
            else:
                return {
                    "status": "offline",
                    "codigo": response.status_code
                }
        except Exception as e:
            return {"erro": str(e)}
    
    def listar_servidores(self):
        """Lista servidores do bot"""
        try:
            response = requests.get(
                f"https://discloud.com/api/rest/app/{BOT_ID}",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                dados = response.json()
                return {
                    "total": dados.get('guilds', 0),
                    "servidores": dados.get('guildsList', [])
                }
            else:
                return {"erro": "Não foi possível listar servidores"}
        except Exception as e:
            return {"erro": str(e)}
    
    def enviar_comando(self, comando):
        """Envia comando para o bot"""
        try:
            # Primeiro verifica se bot está online
            status = requests.get(
                f"https://discloud.com/api/rest/app/{BOT_ID}",
                headers=get_headers(),
                timeout=5
            )
            
            if status.status_code != 200:
                return {
                    "erro": "Bot offline ou não encontrado",
                    "codigo": status.status_code
                }
            
            # Envia comando
            response = requests.post(
                f"https://discloud.com/api/rest/app/{BOT_ID}/cmd",
                headers=get_headers(),
                json={"command": comando},
                timeout=10
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
                    "detalhes": response.text[:100]
                }
        except Exception as e:
            return {"erro": str(e)}