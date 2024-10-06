import discord
from discord import app_commands
import time
import random

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

@tree.command(name="hello", description="Botun selam vermesini sağlar.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Merhaba! Ben Necomen tarafindan yazilan bir Discord botuyum.")

@tree.command(name="info", description="Bot hakkında bilgi verir.")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message("Ben bir botum, çeşitli komutlarla hizmet veriyorum!")

@tree.command(name="say", description="Botun belirttiğiniz bir mesajı söylemesini sağlar.")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@tree.command(name="roll", description="1 ile 100 arasında bir sayı atar.")
async def roll(interaction: discord.Interaction):
    number = random.randint(1, 100)
    await interaction.response.send_message(f"Attığın sayı: {number}")

@tree.command(name="joke", description="Rastgele bir şaka gönderir(bombok oluyo ama).")
async def joke(interaction: discord.Interaction):
    jokes = [
        "Neden bilgisayarlar soğuk olur? Çünkü çok fan var!",
        "Kediler neden bilgisayarı sevmez? Çünkü fareyi kovalarlar!",
        "Süpermen neden asansörü kullanmaz? Çünkü hep yukarıdan gelir!"
    ]
    await interaction.response.send_message(random.choice(jokes))

@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} olarak giriş yapıldı!")


# Botunuzu çalıştırın
client.run('MTI5MjQ4NzMxNDIxOTYwMTkyMA.GmVzAL._UWwSNOtpvPpbEVihV7TdGnm6OnXinrsv0wQT4')