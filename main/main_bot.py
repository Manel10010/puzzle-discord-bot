import discord
from discord import File
import discord.utils
from discord.ext import commands, tasks
from discord import app_commands
import json
from respostas import RESPOSTAS,DICAS
import datetime
import pytz

MY_GUILD = discord.Object(id="ID DO SERVIDOR")  #Servidor


class MyClient(discord.Client):
    def __init__(self, intents:discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self) #Criando a Tree

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    async def on_member_join(self, member):
        print(f"Novo membro {member.mention}")
        log_channel = member.guild.get_channel("ID DO CANAL DE LOG")
        with open("main\data_base.json", 'r+') as file:
            file.seek(0)
            data = json.load(file)
            user_id = str(member.id)
            if user_id not in data.keys():
                file.seek(0)
                data[user_id] = {"dicas":4, "nivel": 0, "erros":0, "acertos": -1} #Por padrão vai ser 4 dicas
                file.write(json.dumps(data)) #Salvando mudança
                await log_channel.send(f"{member.mention} está registrado na data base!")
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f'Bem vindo(a) {member.mention} agora você faz parte do nosso jogo!'
            await guild.system_channel.send(to_send)
    
    async def on_message(self, message):
        pass

def get_tabela(self, url:str):
        with open(url, "r") as file:
            data = json.load(file)
            sorted_data = dict(sorted(data.items(), key=lambda x: x[1]['nivel'], reverse=True))
        return [(key, value['nivel']) for key, value in sorted_data.items()]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True
intents.messages = True
client = MyClient(intents=intents)

@client.event
async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')
        myLoop.start()

def check_role(interaction):
    return interaction.user.Member.get_role("ID DA ROLE ADMIN")

@client.tree.command(name="responder")
async def responder(interaction, message:str):
    """Comando utilizado pra responder os enigmas!"""
    log_channel = interaction.guild.get_channel("ID DO LOG CHANNEL")

    with open("main\data_base.json", 'r+') as file:
        file.seek(0)
        data = json.load(file)
        user_id = str(interaction.user.id)
        nivel_player = int(data[user_id]["nivel"])
        #Validando resposta
        print(RESPOSTAS[nivel_player], message)
        if RESPOSTAS[nivel_player] == message:
            file.seek(0)
            data[user_id]["nivel"]+=1
            data[user_id]["acertos"]+=1
            file.write(json.dumps(data))
            if (data[user_id]["acertos"] == 3):
                file.seek(0)
                data[user_id]["dicas"]+=1
                file.write(json.dumps(data))

                #Embed dica - enviado no pv!
                embed_dica = discord.Embed()
                embed_dica=discord.Embed(title="+1x dica", 
                    description="Por ter acertado 3 respostas seguidas você ganhou mais um uso de dica!", 
                    color=discord.Color.green())
                await interaction.user.send(embed=embed_dica)
            #Log 
            embed_log = discord.Embed(title='Uso do /responder')
            embed_log.description = f'{interaction.user.mention} acertou o enigma #{data[user_id]["nivel"]-1}'
            await log_channel.send(embed=embed_log)

            #Verificando se ele já respondeu tudo
            if data[user_id]["nivel"] >= len(RESPOSTAS):
                await interaction.response.send_message(f"{interaction.user.mention} Você terminou todos os enigmas volte a sala!")
            else:
                file.seek(0)
                data[user_id]["erros"] = 0
                file.write(json.dumps(data))
                #Enviando pro user o embed
                embed=discord.Embed(title="Resposta Correta", 
                    description='', 
                    color=discord.Color.green())
                
                with open(f"main/maps/{int(data[user_id]['nivel'])}.png", 'rb') as f:
                    image = File(f)
                embed.set_image(url=f"attachment://main/maps/{int(data[user_id]['nivel'])}.png")
                await interaction.response.send_message(embed=embed, file=image, ephemeral=True)
        else:
            #Adicionando sequencia de erros
            file.seek(0)
            data[user_id]["erros"]+=1
            data[user_id]["acertos"]=0
            file.write(json.dumps(data))
            embed_log = discord.Embed(title='Uso do /responder')
            embed_log.description = f'{interaction.user.mention} errou o enigma #{data[user_id]["nivel"]}'

            if data[user_id]["erros"] >= 3:
                embed_log.description = f'{interaction.user.mention} errou o enigma #{data[user_id]["nivel"]} e foi punido!'
                embed=discord.Embed(title="Resposta Incorreta", 
                description="Você será punido por errar 3 vezes consecultivamente com um timeout de 1m e 30s", 
                color=discord.Color.red())
                # Define o fuso horário como UTC
                utc_timezone = pytz.timezone('America/Sao_Paulo')

                # Cria um objeto datetime com a data e hora atual em UTC
                utc_now = datetime.datetime.now(tz=utc_timezone)

                # Adiciona 90 segundos ao objeto datetime
                timeout_datetime = utc_now + datetime.timedelta(seconds=90)
                # Espera o tempo limite
                await interaction.user.timeout(timeout_datetime)
                file.seek(0)
                data[user_id]["erros"]=0
                file.write(json.dumps(data))
            else:
                embed=discord.Embed(title="Resposta Incorreta", 
                    color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            await log_channel.send(embed=embed_log)
        
@client.tree.command(name="force_register")
async def force_register(interaction):
    with open("main\data_base.json", 'r+') as file:
            file.seek(0)
            data = json.load(file)
            user_id = str(interaction.user.id)
            if user_id not in data.keys():
                file.seek(0)
                data[user_id] = {"dicas":4, "nivel": 0, "erros":0, "acertos":-1} #Por padrão vai ser 4 dicas
                file.write(json.dumps(data)) #Salvando mudança
                await interaction.response.send_message("Registrado!")


@client.tree.command(name="ajuda")
async def ajuda(interaction):
    """Comando utilizado pra receber dicas do enigma atual! (Existe Limite)"""
    log_channel = interaction.guild.get_channel("ID DO LOG CHANNEL")
    with open("main\data_base.json", 'r+') as file:
        data = json.load(file)
        user_id = str(interaction.user.id)
        nivel_player = int(data[user_id]["nivel"])
        qntd_dicas = int(data[user_id]["dicas"])

        if qntd_dicas > 0:
            embed_log = discord.Embed(title='Uso do /ajuda')
            embed_log.description = f'{interaction.user.mention} usou dica para o enigma #{data[user_id]["nivel"]}'
            await log_channel.send(embed=embed_log)
            file.seek(0)
            #Usa a dica
            data[user_id]["dicas"]-=1
            #Salva o estado
            file.write(json.dumps(data))
            #Cria o embeed
            embed=discord.Embed(title=f"Restam {data[user_id]['dicas']}/4", 
                description=f"Dica: {DICAS[nivel_player]}", 
                color=discord.Color.gold())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed_log = discord.Embed(title='Uso do /ajuda')
            embed_log.description = f'{interaction.user.mention} esgotou suas dicas!'
            await log_channel.send(embed=embed_log)
            embed=discord.Embed(title=f"Dicas esgotadas!", 
                description=f"Vá até o local no mapa pra recuperar!", 
                color=discord.Color.dark_red())
            #embed.set_thumbnail(url="https://i.imgur.com/axLm3p6.jpeg") - Setar os locais de ganho de dicas no mapa da UFAL
            await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.context_menu(name='Reporta pros moderadores')
async def reportar_messagem(interaction: discord.Interaction, message: discord.Message):
    """Reportar mensagens pros moderadores!"""
    await interaction.response.send_message(
        f'Obrigado por reportar essa mensagem de {message.author.mention} para os moderadores.', ephemeral=True
    )

    log_channel = interaction.guild.get_channel("ID DO LOG CHANNEL")

    embed = discord.Embed(title='Menssagem Reportada')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Va até a mensagem', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)

@client.tree.command(name='status')
async def status(interaction):
    embed = discord.Embed()
    embed = discord.Embed(
        title="▬▬STATUS▬▬",
        description="",
        color=discord.Color.dark_gold(),
        url="",
    )
    with open("main\data_base.json", "r") as file:
        file.seek(0)
        data = json.load(file)
        embed.add_field(name=f"Nível: {data[f'{interaction.user.id}']['nivel']}", value='', inline=False)
        embed.add_field(name=f"Dicas: {data[f'{interaction.user.id}']['dicas']}", value='', inline=False)
    await interaction.user.send(embed=embed)
    await interaction.response.send_message("Status enviados na sua DM!", ephemeral=True)

@client.tree.command(name='limpar')
@commands.check(check_role)
async def limpar(interaction, quantidade:int=100):
    """Comando para limpar o chat."""
    channel = interaction.channel
    messages = []
    async for message in channel.history(limit=quantidade):
        messages.append(message)
    await channel.delete_messages(messages)
    await interaction.response.send_message(f'{quantidade} mensagens foram apagadas por {interaction.author.mention}.')

@tasks.loop(minutes=1, seconds=30)
async def myLoop():
    channel = client.get_channel("ID CANAL TABELA") #Canal 'tabela' do discord
    #Pegando tabela atualizada!
    tabela = None
    with open("main\data_base.json", "r") as file:
        data = json.load(file)
        sorted_data = dict(sorted(data.items(), key=lambda x: x[1]['nivel'], reverse=True))
        tabela = [(key, value['nivel']) for key, value in sorted_data.items()]
    #Limpando tabela anterior
    messages = []
    async for message in channel.history(limit=1):
        messages.append(message)
    await channel.delete_messages(messages)
    #Enviando nova tabela
    embed = discord.Embed(
        title="・Ranking Atualizado・",
        description="",
        color=discord.Color.gold()  # Cor do embed em hexadecimal
    )
    embed.set_footer(text="Tabela Colocações:")  # Define um rodapé para o embed
    embed.add_field(name=f"🥇 @{client.get_user(int(tabela[0][0])).name}", value=f"Nível ▬ {tabela[0][1]}",inline=False)
    embed.add_field(name=f"🥈 @{client.get_user(int(tabela[1][0])).name}", value=f"Nível ▬ {tabela[1][1]}", inline=False)
    embed.add_field(name=f"🥉 @{client.get_user(int(tabela[2][0])).name}", value=f"Nível ▬ {tabela[2][1]}", inline=False)
    await channel.send(embed=embed)

client.run("TOKEN DO BOT")
