import discord
import vk_api
from discord.ext import commands
from discord.ui import View, Button
import random
import logging

from config import settings, vktoken
import posting
import pablics
import voice_blast
import sounds

sound_logger_name = "sound_manager"
pablic_logger_name = "pablic_manager"

sound_logger = logging.getLogger(sound_logger_name)
pablic_logger = logging.getLogger(pablic_logger_name)

sound_logger.setLevel(logging.INFO)
pablic_logger.setLevel(logging.INFO)

handler1 = logging.FileHandler(f"logs\{sound_logger_name}.log", mode='a')
handler3 = logging.FileHandler(f"logs\{pablic_logger_name}.log", mode='a')
handler2 = logging.StreamHandler()

formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler1.setFormatter(formatter)
handler2.setFormatter(formatter)
handler3.setFormatter(formatter)

sound_logger.addHandler(handler1)
sound_logger.addHandler(handler2)
pablic_logger.addHandler(handler3)
pablic_logger.addHandler(handler2)

bot = commands.Bot(command_prefix=settings['prefix'], intents=discord.Intents.default().all())


postingObj = posting.Posting()
pablicsObj = pablics.Pablics()
blastingObj = voice_blast.VoiceBlast()


class ChannelNameButton(Button):
    def __init__(self, name, channel, ctx):
        self.channel = channel
        self.name = name
        self.ctx = ctx
        super().__init__(label=name, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if pablicsObj.is_empty(interaction.guild.id):
                await interaction.response.send_message(f"{interaction.user.mention}, на сервере нет пабликов для постинга.")
                return
            if not postingObj.contain_channel(self.channel):
                await interaction.response.send_message(f"{interaction.user.mention}, на {self.channel.name} начался постинг.")
                await postingObj.posting(self.channel)
            else:
                await interaction.response.send_message(f"{interaction.user.mention}, на {self.channel.name} уже есть постинг.")
        else:
            await interaction.response.send_message(f"{interaction.user.mention}, вызови свою панель.")


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
        f'{ctx.message.author.mention} УПРАВЛЕНИЕ ПОСТИНГОМ:\n{settings["prefix"]}start_posting\n{settings["prefix"]}stop_posting\nУПРАВЛЕНИЕ ПАБЛИКАМИ РАССЫЛКИ:\n{settings["prefix"]}add_pablic <<id паблика>> <<тип контента(text или image)>>\n{settings["prefix"]}del_pablic <<id паблика>> <<тип контента(text или image)>>\n{settings["prefix"]}show_pablics\nУПРАВЛЕНИЕ ВОЙС БЛАСТИНГОМ\n{settings["prefix"]}start_voice_blasting\n{settings["prefix"]}stop_voice_blasting\nУПРАВЛЕНИЕ ЗВУКАМИ ДЛЯ ВОЙС БЛАСТИНГА\n{settings["prefix"]}add_sound\n{settings["prefix"]}del_sound <<индекс в списке или название>>\n{settings["prefix"]}show_sounds')


@bot.command()
async def start_posting(ctx):
    server_id = ctx.message.guild.id
    testview = View(timeout=None)
    for channel in bot.get_guild(server_id).channels:
        if channel.type == discord.ChannelType.text:
            testview.add_item(ChannelNameButton(channel.name, channel, ctx))
    await ctx.reply("На какой канал запустить постинг?", view=testview)


@bot.command()
async def stop_posting(ctx):
    server_id = ctx.message.guild.id
    '''for channel in bot.get_guild(server_id).channels:
        if channel.type == discord.ChannelType.text:

            postingObj.posting_channels.remove(channel)'''
    postingObj.del_channel_by_guild_id(server_id)
    await ctx.reply(f"Постинг прекратился")


@bot.command()
async def start_voice_blasting(ctx):
    if ctx.guild in blastingObj.voice_blast_list:
        await ctx.reply(f"На сервере уже есть войс блатинг")
        return

    blastingObj.voice_blast_list.append(ctx.guild)
    await ctx.reply(f"Начался войс бластинг")
    await blastingObj.voice_blasting(ctx.guild)


'''@bot.command()
async def join(ctx: discord.ext.commands.context.Context):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command()
async def leave(ctx: discord.ext.commands.context.Context):
    voice_client = ctx.message.guild.voice_client
    print(ctx.guild.voice_client.client)
    await voice_client.disconnect()


@bot.command()
async def play(ctx):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.play(discord.FFmpegPCMAudio(
            source="D:\creativity\works\programming\8G_bot_discord\sounds\standart\Kunteynir - Блёвбургер.mp3"))
    except:
        await ctx.send("The bot is not connected to a voice channel.")
'''


@bot.command()
async def stop_voice_blasting(ctx):
    for server in blastingObj.voice_blast_list:
        if ctx.guild == server:
            blastingObj.voice_blast_list.remove(ctx.guild)
            await ctx.reply(f"Войс бластинг закончился")
            return
    await ctx.reply(f"На сервере нет войс бластинга")


@bot.command()
async def test(ctx):
    # button = Button(label="Clickme", style=discord.ButtonStyle.secondary,)
    my_view = TestView()
    # my_view.add_item(button)
    await ctx.send("test", view=my_view)


@bot.command()
async def add_pablic(ctx: discord.ext.commands.context.Context, pablic_id, content_type=None):
    vk_session = vk_api.VkApi(token=vktoken)
    session_api = vk_session.get_api()
    try:
        pablic_info = session_api.groups.getById(group_id=int(pablic_id))
    except Exception as er:
        pablic_logger.exception(f"Пользователь - {ctx.message.author.name} ({ctx.message.author.id}), сервер - {ctx.guild.name}/{ctx.channel.name} ({ctx.guild.id}/{ctx.channel.id}): не удалось найти паблик ({pablic_id})")
        await ctx.reply(f'Такого паблика не существует, либо он недоступен')
        return
    response = pablicsObj.add_pablic(int(pablic_id), ctx.guild.id, content_type)
    if response == 0:
        await ctx.reply(f'В {pablic_info[0]["name"]} уже есть этот тип (типы) рассылки')
        pablic_logger.info(
            f"Пользователь - {ctx.message.author.name} ({ctx.message.author.id}), сервер - {ctx.guild.name}/{ctx.channel.name} ({ctx.guild.id}/{ctx.channel.id}): введенные типы уже существуют")
        return
    text = ''
    if pablic_info[0]['is_closed'] == 1:
        try:
            session_api.groups.join(group_id=int(pablic_id))
            text += 'Паблик закрыт - подана заявка на вступление\n'
        except Exception as er:
            text += 'Паблик закрыт и не удается подать заявку\n'
            pablic_logger.exception(f"Пользователь - {ctx.message.author.name} ({ctx.message.author.id}), сервер - {ctx.guild.name}/{ctx.channel.name} ({ctx.guild.id}/{ctx.channel.id}): не удалось подать заявку на {pablic_info[0]['name']} ({pablic_id})")
    await ctx.reply(text + f'В {pablic_info[0]["name"]} добавлено {response} типов')
    pablic_logger.info(f"Пользователь - {ctx.message.author.name} ({ctx.message.author.id}), сервер - {ctx.guild.name}/{ctx.channel.name} ({ctx.guild.id}/{ctx.channel.id}): добавлен паблик {pablic_info[0]['name']} с типами {response}")


@bot.command()
async def del_pablic(ctx: discord.ext.commands.context.Context, pablic_id, content_type=None):
    vk_session = vk_api.VkApi(token=vktoken)
    session_api = vk_session.get_api()

    pablic_info = session_api.groups.getById(group_id=int(pablic_id))
    response = pablicsObj.del_pablic(ctx.guild.id, pablic_id, content_type)
    await ctx.reply(f'С {pablic_info[0]["name"]} удалено {response} типов')
    sound_logger.info(f'Пользователь - {ctx.message.author.name} ({ctx.message.author.id}), сервер - {ctx.guild.name}/{ctx.channel.name} ({ctx.guild.id}/{ctx.channel.id}): с {pablic_info[0]["name"]} удалено {response} типов')


@bot.command()
async def show_pablics(ctx: discord.ext.commands.context.Context):
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


@bot.command()
async def show_sounds(ctx: discord.ext.commands.context.Context):
    sound_obj = sounds.Sounds()
    sound_list = sound_obj.get_sounds(ctx.guild)
    if sound_list == 0 or len(sound_list) == 0:
        await ctx.reply('На сервере нет звуков')
        sound_logger.info(
            f'Пользователь - {ctx.message.author.name} ({ctx.message.author.id}), сервер - {ctx.guild.name}/{ctx.channel.name} ({ctx.guild.id}/{ctx.channel.id}): на сервере нет звуков')
        return
    text_message = ''
    for i in range(len(sound_list)):
        text_message += str(i+1) + " " + sound_list[i] + '\n'
    await ctx.reply(text_message)
    sound_logger.info(
        f'Пользователь - {ctx.message.author.name} ({ctx.message.author.id}), сервер - {ctx.guild.name}/{ctx.channel.name} ({ctx.guild.id}/{ctx.channel.id}): получил список звуков')


@bot.command()
async def add_sound(ctx: discord.ext.commands.context.Context):
    # attachment_message = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.attachments)
    sound_obj = sounds.Sounds()
    if len(ctx.message.attachments) <= 0:
        await ctx.reply('Прикрепи к сообщению с командой файлы.')
        return
    response = sound_obj.add_sound(ctx.guild, ctx.message.attachments)
    if len(response) == 0:
        await ctx.reply('Ни один файл не добавлен.\nФайл должен быть формата mp3, без специфических символов.')
        return
    text_message = 'Добавлен(ы):'
    for i in response:
        text_message += '\n' + i
    sound_logger.info(f'Пользователь - {ctx.message.author.name} ({ctx.message.author.id}), сервер - {ctx.guild.name}/{ctx.channel.name} ({ctx.guild.id}/{ctx.channel.id}): {text_message}')
    await ctx.reply(text_message)


@bot.command()
async def del_sound(ctx: discord.ext.commands.context.Context, name: str):
    sound_obj = sounds.Sounds()
    response = sound_obj.del_sound(ctx.guild, name)
    text = ''
    match response:
        case 0:
            text = 'Такого звука нет на сервере'
            sound_logger.info(f"Звука {name} нет в наличии, по запросу с сервера {ctx.guild.name} ({ctx.guild.id}), пользователь {ctx.message.author.name} ({ctx.message.author.id})")
        case 1:
            text = f"{name} удален с сервера"
            sound_logger.info(f"Удален звук {name} с сервера {ctx.guild.name} ({ctx.guild.id}), пользователь {ctx.message.author.name} ({ctx.message.author.id})")
        case 2:

            text = "Индекс выходит за пределы"
            sound_logger.info(f"Индекс выходит за пределы, сервер {ctx.guild.name} ({ctx.guild.id}), пользователь {ctx.message.author.name} ({ctx.message.author.id})")

    await ctx.reply(text)


@bot.command()
async def test_call(ctx):
    def check(m):
        return m.author.id == ctx.author.id

    await ctx.send('Привет! Ну, что поиграем?😉. Какое число выпадет?(1-6)🎲')

    try:
        # Ожидание ответа от пользователя. timeout - время ожидания.
        answer = await bot.wait_for("message", check=check, timeout=30)
        #print(answer)
        print(answer.attachments)
        answer = answer.content
    except TimeoutError:
        # Если время ожидания вышло.
        return await ctx.send('Время вышло.')


    # await ctx.send(f'Ваша ставка: {amount}')

    # Число от 1 до 6
    '''number = randint(1, 6)

    if re.match(r'[1-6]', answer):
        if number == int(answer):
            await ctx.send('Вы угадали!')
        else:
            return await ctx.send('Вы не угадали.')
    else:
        return await ctx.send('Нужно указать число!')'''


@bot.event
async def on_ready():
    print('ready')


@bot.event
async def on_message_edit(before, after):
    print(f'message changed: {before.content} -> {after.content}')


bot.run(settings['token'])
