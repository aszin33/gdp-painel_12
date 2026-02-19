from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse

# ==================== CONFIGURAÇÕES ====================

DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', '')
BOT_ID = "1386082293533249546"

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = self.path
        print(f"📡 Requisição: {path}")
        
        # ===== ROTA DE TESTE UNIVERSAL =====
        if path == '/api/testar-tudo':
            result = self.testar_todos_endpoints()
        
        # ===== ROTA DE STATUS COM FALLBACK =====
        elif path == '/api/status':
            result = self.status_com_fallback()
        
        # ===== ROTA DE AJUDA =====
        else:
            result = {
                "instrucao": "Use /api/testar-tudo para diagnosticar a conexão com a Discloud",
                "endpoints_disponiveis": [
                    "/api/testar-tudo",
                    "/api/status"
                ]
            }
        
        self.wfile.write(json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def testar_todos_endpoints(self):
        """Testa todas as possíveis variações da API da Discloud"""
        
        if not DISCLOUD_TOKEN:
            return {
                "erro": "Token não configurado",
                "instrucao": "Configure DISCLOUD_TOKEN na Vercel"
            }
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        # Lista de possíveis endpoints e métodos
        testes = [
            # API v1
            {"nome": "API v1 - User", "url": "https://api.discloud.com/v1/user", "metodo": "GET"},
            {"nome": "API v1 - Apps", "url": "https://api.discloud.com/v1/apps", "metodo": "GET"},
            {"nome": "API v1 - App", "url": f"https://api.discloud.com/v1/app/{BOT_ID}", "metodo": "GET"},
            
            # API sem versão
            {"nome": "API - User", "url": "https://api.discloud.com/user", "metodo": "GET"},
            {"nome": "API - Apps", "url": "https://api.discloud.com/apps", "metodo": "GET"},
            {"nome": "API - App", "url": f"https://api.discloud.com/app/{BOT_ID}", "metodo": "GET"},
            
            # REST antigo
            {"nome": "REST - User", "url": "https://discloud.com/api/rest/user", "metodo": "GET"},
            {"nome": "REST - Apps", "url": "https://discloud.com/api/rest/apps", "metodo": "GET"},
            {"nome": "REST - App", "url": f"https://discloud.com/api/rest/app/{BOT_ID}", "metodo": "GET"},
            
            # Alternativas
            {"nome": "Status API", "url": "https://discloud.com/api/status", "metodo": "GET"},
            {"nome": "Ping", "url": "https://discloud.com/api/ping", "metodo": "GET"},
        ]
        
        resultados = []
        
        for teste in testes:
            try:
                print(f"🔄 Testando: {teste['nome']}")
                print(f"   URL: {teste['url']}")
                
                response = requests.request(
                    metodo=teste['metodo'],
                    url=teste['url'],
                    headers=headers,
                    timeout=10
                )
                
                resultado = {
                    "teste": teste['nome'],
                    "url": teste['url'],
                    "status": response.status_code,
                    "funcionou": response.status_code == 200
                }
                
                if response.status_code == 200:
                    try:
                        dados = response.json()
                        resultado["resposta"] = str(dados)[:100] + "..."
                    except:
                        resultado["resposta"] = response.text[:100] + "..."
                else:
                    resultado["erro"] = f"HTTP {response.status_code}"
                
                resultados.append(resultado)
                
            except requests.exceptions.ConnectionError:
                resultados.append({
                    "teste": teste['nome'],
                    "erro": "Erro de conexão"
                })
            except Exception as e:
                resultados.append({
                    "teste": teste['nome'],
                    "erro": str(e)
                })
        
        # Analisar resultados
        endpoints_funcionando = [r for r in resultados if r.get('funcionou')]
        
        if endpoints_funcionando:
            conclusao = f"✅ Encontrados {len(endpoints_funcionando)} endpoints funcionando!"
            melhor_endpoint = endpoints_funcionando[0]['url'].split('/api')[0] + "/api"
        else:
            conclusao = "❌ Nenhum endpoint funcionou. O token pode ser inválido."
            melhor_endpoint = None
        
        return {
            "token": {
                "configurado": True,
                "preview": DISCLOUD_TOKEN[:30] + "...",
                "tamanho": len(DISCLOUD_TOKEN)
            },
            "bot_id": BOT_ID,
            "resultados": resultados,
            "analise": {
                "total_testes": len(testes),
                "sucessos": len(endpoints_funcionando),
                "falhas": len(testes) - len(endpoints_funcionando),
                "conclusao": conclusao,
                "endpoint_recomendado": melhor_endpoint
            },
            "proximos_passos": [
                "Se nenhum endpoint funcionou: seu token é inválido",
                "Se alguns funcionaram: vamos usar o endpoint correto",
                "Depois de identificar, use /api/status para ver o bot"
            ]
        }
    
    def status_com_fallback(self):
        """Tenta status em vários endpoints até achar um que funcione"""
        
        endpoints = [
            f"https://discloud.com/api/rest/app/{BOT_ID}",
            f"https://api.discloud.com/v1/app/{BOT_ID}",
            f"https://api.discloud.com/app/{BOT_ID}"
        ]
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        for url in endpoints:
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    dados = response.json()
                    return {
                        "status": "online",
                        "endpoint_usado": url,
                        "nome": dados.get('name', 'Desconhecido'),
                        "servidores": dados.get('guilds', 0)
                    }
            except:
                continue
        
        return {
            "status": "offline",
            "erro": "Não foi possível conectar em nenhum endpoint",
            "instrucao": "Use /api/testar-tudo para diagnóstico completo"
        }