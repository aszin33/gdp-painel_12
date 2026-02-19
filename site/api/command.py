from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse
import time

# ==================== CONFIGURAÇÕES ====================

DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyOTcwNzEyNTkzNzY0MjI5NjciLCJrZXkiOiJLS2JnM3UifQ.r69UTZ4HsT-oppc1RjdEKiFBS0z3vCR8tXZB_L-l2Sw')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')

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
        
        print(f"📡 Requisição recebida: {path}")
        print(f"🔑 Token configurado: {'Sim' if DISCLOUD_TOKEN else 'Não'}")
        
        # ========== ROTA PRINCIPAL ==========
        if path == '/' or path == '/api' or path == '/api/':
            result = self.rota_principal()
        
        # ========== ROTA DE TESTE ==========
        elif path == '/api/test':
            result = self.rota_teste()
        
        # ========== ROTA PARA VERIFICAR TOKEN ==========
        elif path == '/api/verificar-token':
            result = self.verificar_token()
        
        # ========== ROTA PARA TESTAR MÚLTIPLOS ENDPOINTS ==========
        elif path == '/api/testar-endpoints':
            result = self.testar_endpoints()
        
        # ========== ROTA DE STATUS DO BOT ==========
        elif path == '/api/status':
            # Primeiro verifica token
            if not DISCLOUD_TOKEN:
                result = {"status": "offline", "erro": "Token não configurado"}
            else:
                result = self.status_bot()
        
        # ========== ROTA DE INFORMAÇÕES DO BOT ==========
        elif path == '/api/info':
            if not DISCLOUD_TOKEN:
                result = {"erro": "Token não configurado"}
            else:
                result = self.info_bot()
        
        # ========== ROTA PARA ENVIAR COMANDO GDP ==========
        elif path.startswith('/api/gdp/'):
            if not DISCLOUD_TOKEN:
                result = {"erro": "Token não configurado"}
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
            if not DISCLOUD_TOKEN:
                result = {"erro": "Token não configurado"}
            else:
                partes = path.split('/')
                if len(partes) >= 4:
                    server_id = partes[3]
                    result = self.enviar_comando(f"!nuclear {server_id}")
                else:
                    result = {"erro": "URL inválida. Use: /api/nuclear/ID_DO_SERVIDOR"}
        
        # ========== ROTA NÃO ENCONTRADA ==========
        else:
            result = {
                "erro": "Rota não encontrada",
                "rotas_disponiveis": [
                    "/api",
                    "/api/test",
                    "/api/verificar-token",
                    "/api/testar-endpoints",
                    "/api/status",
                    "/api/info",
                    "/api/gdp/ID/QUANTIDADE",
                    "/api/nuclear/ID"
                ]
            }
        
        # Enviar resposta
        self.wfile.write(json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Responde a requisições OPTIONS (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()
    
    # ==================== FUNÇÕES PRINCIPAIS ====================
    
    def rota_principal(self):
        """Rota inicial da API"""
        return {
            "nome": "GDP Control API",
            "versao": "4.0",
            "status": "online",
            "token": {
                "configurado": bool(DISCLOUD_TOKEN),
                "preview": DISCLOUD_TOKEN[:30] + "..." if DISCLOUD_TOKEN else None
            },
            "bot_id": BOT_ID,
            "endpoints": {
                "testar_token": "/api/verificar-token",
                "testar_endpoints": "/api/testar-endpoints",
                "status_bot": "/api/status",
                "info_bot": "/api/info",
                "comando_gdp": "/api/gdp/ID_DO_SERVIDOR/QUANTIDADE",
                "comando_nuclear": "/api/nuclear/ID_DO_SERVIDOR"
            }
        }
    
    def rota_teste(self):
        """Rota de teste simples"""
        return {
            "status": "online",
            "mensagem": "API funcionando corretamente",
            "timestamp": time.time(),
            "token_configurado": bool(DISCLOUD_TOKEN),
            "bot_id": BOT_ID
        }
    
    def verificar_token(self):
        """Verifica se o token é válido testando endpoint /user"""
        
        if not DISCLOUD_TOKEN:
            return {
                "valido": False,
                "erro": "Token não configurado",
                "instrucao": "Configure a variável DISCLOUD_TOKEN na Vercel"
            }
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        try:
            # Testar endpoint do usuário
            response = requests.get(
                "https://discloud.com/api/rest/user",
                headers=headers,
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
                    "instrucao": "Gere um novo token no site da Discloud",
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
    
    def testar_endpoints(self):
        """Testa múltiplos endpoints da Discloud para diagnóstico"""
        
        if not DISCLOUD_TOKEN:
            return {"erro": "Token não configurado"}
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        # Lista de endpoints para testar
        endpoints = [
            {
                "nome": "API Rest - User",
                "url": "https://discloud.com/api/rest/user",
                "metodo": "GET",
                "importante": True
            },
            {
                "nome": "API Rest - Apps",
                "url": "https://discloud.com/api/rest/apps",
                "metodo": "GET",
                "importante": True
            },
            {
                "nome": "API Rest - App",
                "url": f"https://discloud.com/api/rest/app/{BOT_ID}",
                "metodo": "GET",
                "importante": True
            },
            {
                "nome": "API v1 - User",
                "url": "https://api.discloud.com/v1/user",
                "metodo": "GET",
                "importante": False
            },
            {
                "nome": "API v1 - Apps",
                "url": "https://api.discloud.com/v1/apps",
                "metodo": "GET",
                "importante": False
            },
            {
                "nome": "API Status",
                "url": "https://discloud.com/api/status",
                "metodo": "GET",
                "importante": False
            }
        ]
        
        resultados = []
        
        for ep in endpoints:
            try:
                print(f"🔄 Testando: {ep['nome']}")
                print(f"   URL: {ep['url']}")
                
                if ep['metodo'] == 'GET':
                    response = requests.get(ep['url'], headers=headers, timeout=10)
                else:
                    response = requests.post(ep['url'], headers=headers, timeout=10)
                
                info = {
                    "endpoint": ep['nome'],
                    "url": ep['url'],
                    "status": response.status_code,
                    "funcionou": response.status_code == 200
                }
                
                if response.status_code == 200:
                    try:
                        dados = response.json()
                        info["resumo"] = str(dados)[:100] + "..."
                    except:
                        info["resumo"] = response.text[:100] + "..."
                else:
                    info["erro"] = f"HTTP {response.status_code}"
                    info["resposta"] = response.text[:100] + "..."
                
                resultados.append(info)
                
            except requests.exceptions.ConnectionError:
                resultados.append({
                    "endpoint": ep['nome'],
                    "erro": "Erro de conexão"
                })
            except Exception as e:
                resultados.append({
                    "endpoint": ep['nome'],
                    "erro": str(e)
                })
        
        # Analisar resultados
        sucessos = [r for r in resultados if r.get('funcionou')]
        
        if sucessos:
            conclusao = f"✅ {len(sucessos)} endpoints funcionando!"
            token_valido = True
        else:
            conclusao = "❌ Nenhum endpoint funcionou. Token inválido."
            token_valido = False
        
        return {
            "token": {
                "configurado": True,
                "preview": DISCLOUD_TOKEN[:30] + "...",
                "tamanho": len(DISCLOUD_TOKEN)
            },
            "bot_id": BOT_ID,
            "testes": resultados,
            "resumo": {
                "total": len(endpoints),
                "sucessos": len(sucessos),
                "falhas": len(endpoints) - len(sucessos),
                "token_valido": token_valido,
                "conclusao": conclusao
            }
        }
    
    def status_bot(self):
        """Verifica status do bot específico"""
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        try:
            response = requests.get(
                f"https://discloud.com/api/rest/app/{BOT_ID}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                dados = response.json()
                return {
                    "status": "online",
                    "nome": dados.get('name', 'Desconhecido'),
                    "id": BOT_ID,
                    "servidores": dados.get('guilds', 0),
                    "usuarios": dados.get('users', 0),
                    "ram": dados.get('ram', '100MB'),
                    "online_desde": dados.get('onlineSince', ''),
                    "comandos_executados": dados.get('commands', 0)
                }
            elif response.status_code == 404:
                return {
                    "status": "offline",
                    "erro": "Bot não encontrado",
                    "codigo": 404,
                    "instrucao": "Verifique se o BOT_ID está correto ou se o bot está hospedado"
                }
            else:
                return {
                    "status": "offline",
                    "codigo": response.status_code,
                    "erro": response.text[:100]
                }
        except Exception as e:
            return {
                "status": "offline",
                "erro": str(e)
            }
    
    def info_bot(self):
        """Informações detalhadas do bot"""
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        try:
            response = requests.get(
                f"https://discloud.com/api/rest/app/{BOT_ID}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "online",
                    "dados_completos": response.json()
                }
            else:
                return {
                    "status": "offline",
                    "codigo": response.status_code,
                    "dados": response.text[:200]
                }
        except Exception as e:
            return {"erro": str(e)}
    
    def enviar_comando(self, comando):
        """Envia um comando para o bot"""
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        try:
            # Primeiro verifica se o bot está online
            status = requests.get(
                f"https://discloud.com/api/rest/app/{BOT_ID}",
                headers=headers,
                timeout=5
            )
            
            if status.status_code != 200:
                return {
                    "erro": "Bot offline ou não encontrado",
                    "codigo": status.status_code
                }
            
            # Envia o comando
            response = requests.post(
                f"https://discloud.com/api/rest/app/{BOT_ID}/cmd",
                headers=headers,
                json={"command": comando},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "sucesso": True,
                    "comando": comando,
                    "mensagem": "Comando enviado com sucesso!"
                }
            else:
                return {
                    "erro": f"Erro {response.status_code}",
                    "detalhes": response.text[:100]
                }
        except Exception as e:
            return {"erro": str(e)}