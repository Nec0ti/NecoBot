import os
import discord
from discord import app_commands
import time
import random
import requests
from flask import Flask, render_template_string
from datetime import datetime, timedelta
import json
import threading

app = Flask(__name__)

# Bu değişkenler normalde veritabanında saklanır, 
# ancak bu örnekte basitlik için global değişkenler kullanıyoruz
command_usage = {}
last_command = {"name": "None", "time": "Never"}
total_commands_last_hour = 0

@app.route('/')
def home():
    global command_usage, last_command, total_commands_last_hour
    
    # Son 1 saatteki komut kullanımını hesapla
    one_hour_ago = datetime.now() - timedelta(hours=1)
    total_commands_last_hour = sum(1 for cmd in command_usage.values() for time in cmd['times'] if time > one_hour_ago)
    
    # Komut kullanım verilerini JSON'a çevir
    command_data = json.dumps({cmd: len(times) for cmd, times in command_usage.items()})
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Discord Bot Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #7289da; }
            .stat { margin-bottom: 20px; }
            .stat h2 { margin-bottom: 5px; }
            .stat p { margin-top: 0; font-size: 1.2em; }
            canvas { max-width: 100%; height: auto; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Discord Bot Dashboard</h1>
            <div class="stat">
                <h2>Bot Status</h2>
                <p>Online</p>
            </div>
            <div class="stat">
                <h2>Last Used Command</h2>
                <p>{{ last_command['name'] }} ({{ last_command['time'] }})</p>
            </div>
            <div class="stat">
                <h2>Commands Used in Last Hour</h2>
                <p>{{ total_commands_last_hour }}</p>
            </div>
            <div class="stat">
                <h2>Command Usage</h2>
                <canvas id="commandChart"></canvas>
            </div>
        </div>
        
        <script>
            var ctx = document.getElementById('commandChart').getContext('2d');
            var commandData = JSON.parse('{{ command_data | safe }}');
            var chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(commandData),
                    datasets: [{
                        label: 'Command Usage',
                        data: Object.values(commandData),
                        backgroundColor: 'rgba(114, 137, 218, 0.5)',
                        borderColor: 'rgba(114, 137, 218, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            precision: 0
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    ''', command_data=command_data, last_command=last_command, total_commands_last_hour=total_commands_last_hour)

# Bu fonksiyon, bir komut kullanıldığında çağrılmalı
def update_command_usage(command_name):
    global command_usage, last_command, total_commands_last_hour
    now = datetime.now()
    if command_name not in command_usage:
        command_usage[command_name] = {"times": []}
    command_usage[command_name]["times"].append(now)
    last_command["name"] = command_name
    last_command["time"] = now.strftime("%Y-%m-%d %H:%M:%S")

    # Son 1 saatteki komutları temizle
    one_hour_ago = now - timedelta(hours=1)
    for cmd in command_usage.values():
        cmd["times"] = [time for time in cmd["times"] if time > one_hour_ago]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="ping", description="Botun gecikme süresini ölçer")
async def ping(interaction: discord.Interaction):
    try:
        start_time = time.time()
        await interaction.response.send_message("Ping ölçülüyor...")
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        await interaction.edit_original_response(content=f"Pong! Gecikme: {latency}ms")
        update_command_usage("ping")
    except Exception as e:
        await interaction.response.send_message(f"Bir hata oluştu: {str(e)}", ephemeral=True)

@tree.command(name="hello", description="Botun selam vermesini sağlar.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Merhaba! Ben Necomen tarafindan yazilan bir Discord botuyum.")
    update_command_usage("hello")

@tree.command(name="info", description="Bot hakkında bilgi verir.")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message("Ben bir botum, çeşitli komutlarla hizmet veriyorum!")
    update_command_usage("info")

@tree.command(name="say", description="Botun belirttiğiniz bir mesajı söylemesini sağlar.")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)
    update_command_usage("say")

@tree.command(name="roll", description="1 ile 100 arasında bir sayı atar.")
async def roll(interaction: discord.Interaction):
    number = random.randint(1, 100)
    await interaction.response.send_message(f"Attığın sayı: {number}")
    update_command_usage("roll")

@tree.command(name="joke", description="Rastgele bir meme fotosu gönderir.")
async def joke(interaction: discord.Interaction):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as response:
                if response.status == 200:
                    data = await response.json()
                    meme_url = data['url']
                    await interaction.response.send_message(meme_url)
                else:
                    await interaction.response.send_message("Meme çekilemedi. Lütfen tekrar deneyin.")
    except Exception as e:
        await interaction.response.send_message(f"Bir hata oluştu: {str(e)}", ephemeral=True)
    finally:
        update_command_usage("joke")

@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} olarak giriş yapıldı!")

def run_discord_bot():
    client.run(os.getenv('TOKEN'))

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    discord_thread = threading.Thread(target=run_discord_bot)
    flask_thread = threading.Thread(target=run_flask)
    
    discord_thread.start()
    flask_thread.start()
    
    discord_thread.join()
    flask_thread.join()

# client.run('MTI5MjQ4NzMxNDIxOTYwMTkyMA.GmVzAL._UWwSNOtpvPpbEVihV7TdGnm6OnXinrsv0wQT4')
