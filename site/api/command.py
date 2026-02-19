from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse

# ==================== CONFIGURAÇÕES ====================

DISCLOUD_TOKEN = os.getenv('DISCLOUD_TOKEN', '')
BOT_ID_DISCORD = "1386082293533249546"  # Este é o ID do Discord (pode não ser o da Discloud)

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = self.path
        print(f"📡 Requisição: {path}")
        
        # ===== ROTA PARA DESCOBRIR ID CORRETO =====
        if path == '/api/descobrir-id':
            result = self.descobrir_id_bot()
        
        # ===== ROTA PARA LISTAR TODOS OS BOTS =====
        elif path == '/api/meus-bots':
            result = self.listar_meus_bots()
        
        # ===== ROTA DE STATUS COM ID AUTOMÁTICO =====
        elif path == '/api/status':
            # Primeiro tenta descobrir o ID correto
            id_correto = self.encontrar_id_correto()
            if id_correto:
                result = self.status_bot(id_correto)
            else:
                result = {
                    "status": "offline",
                    "erro": "Não foi possível encontrar seu bot na Discloud",
                    "instrucao": "Use /api/meus-bots para ver todos seus bots"
                }
        
        # ===== ROTA PARA ENVIAR COMANDO =====
        elif path.startswith('/api/comando/'):
            # /api/comando/ID_SERVIDOR/!gdp%20100
            import urllib.parse
            partes = path.split('/')
            if len(partes) >= 4:
                server_id = partes[3]
                comando = urllib.parse.unquote(partes[4]) if len(partes) >= 5 else "!gdp 100"
                
                id_correto = self.encontrar_id_correto()
                if id_correto:
                    result = self.enviar_comando(id_correto, f"{comando} {server_id}")
                else:
                    result = {"erro": "Bot não encontrado na Discloud"}
            else:
                result = {"erro": "URL inválida"}
        
        else:
            result = {
                "rotas": [
                    "/api/descobrir-id",
                    "/api/meus-bots",
                    "/api/status",
                    "/api/comando/ID_SERVIDOR/COMANDO"
                ],
                "instrucao": "Primeiro use /api/descobrir-id para encontrar seu bot"
            }
        
        self.wfile.write(json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def descobrir_id_bot(self):
        """Tenta descobrir qual é o ID correto do bot na Discloud"""
        
        if not DISCLOUD_TOKEN:
            return {"erro": "Token não configurado"}
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        try:
            # Tenta listar todos os apps do usuário
            response = requests.get(
                "https://discloud.com/api/rest/apps",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                dados = response.json()
                apps = dados.get('apps', [])
                
                if apps:
                    # Tem apps listados
                    resultado = {
                        "token_valido": True,
                        "total_bots": len(apps),
                        "seus_bots": []
                    }
                    
                    for app in apps:
                        app_id = app.get('id')
                        app_name = app.get('name')
                        app_status = app.get('status')
                        
                        resultado["seus_bots"].append({
                            "id": app_id,
                            "nome": app_name,
                            "status": app_status,
                            "id_discord": BOT_ID_DISCORD,
                            "correspondencia": app_id == BOT_ID_DISCORD
                        })
                    
                    return resultado
                else:
                    return {
                        "token_valido": True,
                        "mensagem": "Token válido mas nenhum bot encontrado",
                        "instrucao": "Você precisa hospedar um bot na Discloud primeiro"
                    }
            
            elif response.status_code == 401:
                return {
                    "token_valido": False,
                    "erro": "Token inválido",
                    "instrucao": "Gere um novo token no site da Discloud"
                }
            else:
                return {
                    "token_valido": False,
                    "status": response.status_code,
                    "resposta": response.text[:200]
                }
                
        except Exception as e:
            return {"erro": str(e)}
    
    def listar_meus_bots(self):
        """Lista todos os bots do usuário"""
        
        headers = {'api-token': DISCLOUD_TOKEN}
        
        try:
            response = requests.get(
                "https://discloud.com/api/rest/apps",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "erro": f"Erro {response.status_code}",
                    "detalhe": response.text[:200]
                }
        except Exception as e:
            return {"erro": str(e)}
    
    def encontrar_id_correto(self):
        """Tenta encontrar o ID correto do bot"""
        try:
            headers = {'api-token': DISCLOUD_TOKEN}
            response = requests.get(
                "https://discloud.com/api/rest/apps",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                dados = response.json()
                apps = dados.get('apps', [])
                
                # Procura por correspondência com o ID do Discord
                for app in apps:
                    if app.get('id') == BOT_ID_DISCORD:
                        return app.get('id')
                
                # Se não achou, pega o primeiro
                if apps:
                    return apps[0].get('id')
            
            return None
        except:
            return None
    
    def status_bot(self, bot_id):
        """Pega status de um bot específico"""
        headers = {'api-token': DISCLOUD_TOKEN}
        
        try:
            response = requests.get(
                f"https://discloud.com/api/rest/app/{bot_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                dados = response.json()
                return {
                    "status": "online",
                    "id": bot_id,
                    "nome": dados.get('name', 'Desconhecido'),
                    "servidores": dados.get('guilds', 0),
                    "ram": dados.get('ram', '100MB')
                }
            else:
                return {
                    "status": "offline",
                    "id": bot_id,
                    "codigo": response.status_code
                }
        except Exception as e:
            return {"erro": str(e)}
    
    def enviar_comando(self, bot_id, comando):
        """Envia comando para o bot"""
        headers = {'api-token': DISCLOUD_TOKEN}
        
        try:
            response = requests.post(
                f"https://discloud.com/api/rest/app/{bot_id}/cmd",
                headers=headers,
                json={"command": comando},
                timeout=10
            )
            
            if response.status_code == 200:
                return {"sucesso": True, "comando": comando}
            else:
                return {"erro": f"Erro {response.status_code}"}
        except Exception as e:
            return {"erro": str(e)}