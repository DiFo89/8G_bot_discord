import discord
import vk_api
import os
from discord.interactions import Interaction
from discord.ext import commands
from discord.ui import View, Button

from config import settings, vktoken
import posting
import pablics
import voice_blast

bot = commands.Bot(command_prefix=settings['prefix'], intents=discord.Intents.all())

postingObj = posting.Posting()
pablicsObj = pablics.Pablics()
blastingObj = voice_blast.VoiceBlast()


class ChannelNameButton(Button):
    def __init__(self, name, channel, ctx):
        self.channel = channel
        self.name = name
        self.ctx = ctx
        super().__init__(label=name, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction):
        if interaction.user == self.ctx.author:
            if self.channel not in postingObj.posting_channels:
                postingObj.posting_channels.append(self.channel)
                await interaction.response.send_message(f"На {self.channel.name} начался постинг")
                await postingObj.posting(self.channel)

            else:
                await interaction.response.send_message(f"На {self.channel.name} уже есть постинг")
        else:
            await interaction.response.send_message("Вызови свою панель")


class TestView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="0", style=discord.ButtonStyle.danger, custom_id="counter_button")
    async def counter(self, interaction: discord.Interaction, button: discord.ui.Button):
        label = int(button.label)
        label += 1
        button.label = str(label)
        await interaction.response.edit_message(view=self)


@bot.command(aliases=['привет', 'здаров'])
async def hello(ctx):
    author = ctx.message.author

    await ctx.send(f'Hello, {author.mention}!')


@bot.command(aliases=['хелп', 'помощь'])
async def helpme(ctx):
    await ctx.send(
        f'{ctx.message.author.mention} УПРАВЛЕНИЕ ПОСТИНГОМ:\n{settings["prefix"]}start_posting\n{settings["prefix"]}stop_posting\nУПРАВЛЕНИЕ ПАБЛИКАМИ РАССЫЛКИ:\n{settings["prefix"]}add_pablic <<id паблика>> <<тип контента(text или image)>>\n{settings["prefix"]}del_pablic <<id паблика>> <<тип контента(text или image)>>\n{settings["prefix"]}show_pablics')


@bot.command()
async def start_posting(ctx):
    server_id = ctx.message.guild.id
    channel_list = []
    for channel in bot.get_guild(server_id).channels:
        if channel.type == discord.ChannelType.text:
            channel_list.append(channel)

    testview = View(timeout=None)
    for mychannel in channel_list:
        button = ChannelNameButton(mychannel.name, mychannel, ctx)
        testview.add_item(button)
    await ctx.send("На какой канал запустить постинг?", view=testview)


@bot.command()
async def stop_posting(ctx):
    server_id = ctx.message.guild.id
    channel_list = []
    for channel in bot.get_guild(server_id).channels:
        if channel.type == discord.ChannelType.text:
            channel_list.append(channel)
    for channel in channel_list:
        if channel in postingObj.posting_channels:
            postingObj.posting_channels.remove(channel)


@bot.command()
async def start_voice_blasting(ctx):
    blastingObj.voice_blast_list.append(ctx.guild)
    await ctx.send("Начался особый ивент")
    await blastingObj.voice_blasting(ctx.guild)


@bot.command()
async def stop_voice_blasting(ctx):
    blastingObj.voice_blast_list.remove(ctx.guild)
    await ctx.send("Особый ивент закончился")


@bot.command()
async def test(ctx):
    # button = Button(label="Clickme", style=discord.ButtonStyle.secondary,)
    my_view = TestView()
    # my_view.add_item(button)
    await ctx.send("test", view=my_view)


@bot.command()
async def add_pablic(ctx, pablic_id, content_type=None):
    vk_session = vk_api.VkApi(token=vktoken)
    session_api = vk_session.get_api()
    try:
        pablic_info = session_api.groups.getById(group_id=int(pablic_id))
    except Exception as er:
        print(f'Error: {str(er)}')
        await ctx.reply(f'Такого паблика не существует, либо он не доступен')
        return
    response = pablicsObj.add_pablic(int(pablic_id), ctx.guild.id, content_type)
    if response > 0 and pablic_info[0]['is_closed'] == 0:
        try:
            session_api.groups.join(group_id=int(pablic_id))
        except Exception as er:
            print(f'Error: {str(er)}')
    await ctx.reply(f'В {pablic_info[0]["name"]} добавлено {response} типов')
    print(f'add {response}')


@bot.command()
async def del_pablic(ctx, pablic_id, content_type=None):
    vk_session = vk_api.VkApi(token=vktoken)
    session_api = vk_session.get_api()

    pablic_info = session_api.groups.getById(group_id=int(pablic_id))
    response = pablicsObj.del_pablic(ctx.guild.id, pablic_id, content_type)
    await ctx.reply(f'С {pablic_info[0]["name"]} удалено {response} типов')
    print(f'del {response}')


@bot.command()
async def show_pablics(ctx):
    response = pablicsObj.get_pablics(ctx.guild.id)
    if response == 0:
        await ctx.reply('На сервере нет пабликов для рассылки')
        return
    vk_session = vk_api.VkApi(token=vktoken)
    session_api = vk_session.get_api()

    pablics_info = session_api.groups.getById(group_ids=[pablic['id'] for pablic in response])

    pablic_names = [group['name'] for group in pablics_info]
    text_message = "Паблики: \n\n"
    i = 0
    length = len(response)
    while i < length:
        text_message += str(response[i]['id']) + ": \t" + response[i]['type']
        for j in range(length):
            if response[j]['id'] == response[i]['id'] and response[i]['type'] != response[j]['type']:
                text_message += ", " + response[j]['type']
                response.remove(response[j])
                length -= 1
                break
        text_message += "\t" + pablic_names[i] + "\n"
        i += 1
    await ctx.reply(text_message)


@bot.event
async def on_ready():
    print('ready')


@bot.event
async def on_message_edit(before, after):
    print(f'message changed: {before.content} -> {after.content}')


bot.run(settings['token'])
