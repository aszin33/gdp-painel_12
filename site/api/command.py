from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse
import time

# ==================== CONFIGURAÇÕES ====================
DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyOTcwNzEyNTkzNzY0MjI5NjciLCJrZXkiOiJLS2JnM3UifQ.r69UTZ4HsT-oppc1RjdEKiFBS0z3vCR8tXZB_L-l2Sw')
BOT_ID = os.getenv('BOT_ID', '1386082293533249546')
API_BASE_URL = "https://api.discloud.app/v2"  # <-- NOVA URL DA API

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
        elif path == '/api/info':
            result = self.info_bot()
        elif path.startswith('/api/gdp/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                quantidade = partes[4] if len(partes) >= 5 else '100'
                result = self.enviar_comando(f"!gdp {quantidade} {server_id}")
            else:
                result = {"erro": "URL inválida. Use: /api/gdp/ID/QUANTIDADE"}
        elif path.startswith('/api/nuclear/'):
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                result = self.enviar_comando(f"!nuclear {server_id}")
            else:
                result = {"erro": "URL inválida. Use: /api/nuclear/ID"}
        else:
            result = {"erro": "Rota não encontrada", "rotas_disponiveis": ["/api", "/api/test", "/api/verificar-token", "/api/status", "/api/info", "/api/gdp/ID/QUANTIDADE", "/api/nuclear/ID"]}

        self.wfile.write(json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api-token')
        self.end_headers()

    # ==================== FUNÇÕES AUXILIARES ====================
    def _fazer_requisicao(self, metodo, endpoint, dados=None):
        """Faz uma requisição para a nova API da Discloud."""
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
        except requests.exceptions.ConnectionError:
            return {"sucesso": False, "erro": "Erro de conexão com a Discloud"}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    # ==================== ROTAS IMPLEMENTADAS ====================
    def rota_principal(self):
        return {"nome": "GDP Control API", "versao": "5.0 (API v2)", "status": "online", "token_configurado": bool(DISCLOUD_TOKEN)}

    def rota_teste(self):
        return {"status": "online", "mensagem": "API funcionando com a nova versão da Discloud", "timestamp": time.time()}

    def verificar_token(self):
        if not DISCLOUD_TOKEN:
            return {"valido": False, "erro": "Token não configurado"}
        resultado = self._fazer_requisicao('GET', '/user')
        if resultado['sucesso']:
            return {"valido": True, "dados": resultado['dados']}
        else:
            return {"valido": False, "erro": resultado.get('erro'), "status": resultado.get('status')}

    def status_bot(self):
        if not DISCLOUD_TOKEN:
            return {"status": "offline", "erro": "Token não configurado"}
        # Usa o endpoint /app/{appID}/status para verificar o status
        resultado = self._fazer_requisicao('GET', f"/app/{BOT_ID}/status")
        if resultado['sucesso']:
            return {"status": "online", "dados": resultado['dados']}
        else:
            return {"status": "offline", "erro": resultado.get('erro'), "codigo": resultado.get('status')}

    def info_bot(self):
        if not DISCLOUD_TOKEN:
            return {"erro": "Token não configurado"}
        resultado = self._fazer_requisicao('GET', f"/app/{BOT_ID}")
        if resultado['sucesso']:
            return {"status": "online", "dados": resultado['dados']}
        else:
            return {"status": "offline", "erro": resultado.get('erro')}

    def enviar_comando(self, comando):
        if not DISCLOUD_TOKEN:
            return {"erro": "Token não configurado"}
        # Usa o endpoint /app/{appID}/exec para executar comandos
        resultado = self._fazer_requisicao('PUT', f"/app/{BOT_ID}/exec", dados={"cmd": comando})
        if resultado['sucesso']:
            return {"sucesso": True, "comando": comando, "resposta": resultado['dados']}
        else:
            return {"erro": f"Erro ao enviar comando: {resultado.get('erro')}"}