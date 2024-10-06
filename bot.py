import discord
from discord import app_commands
import time

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="ping", description="Botun gecikme süresini ölçer")
async def ping(interaction: discord.Interaction):
    start_time = time.time()
    await interaction.response.send_message("Ping ölçülüyor...")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000)
    await interaction.edit_original_response(content=f"Pong! Gecikme: {latency}ms")

@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} olarak giriş yapıldı!")


# Botunuzu çalıştırın
client.run('MTI5MjQ4NzMxNDIxOTYwMTkyMA.GmVzAL._UWwSNOtpvPpbEVihV7TdGnm6OnXinrsv0wQT4')