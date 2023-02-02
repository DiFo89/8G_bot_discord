import discord
import vk_api
from discord.ext import commands
from discord.ui import View, Button

from config import settings, vktoken
import posting
import pablics
import voice_blast
import sounds

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
            await interaction.response.send_message(f"{interaction.user.mention}, вызови свою панель")


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
        f'{ctx.message.author.mention} УПРАВЛЕНИЕ ПОСТИНГОМ:\n{settings["prefix"]}start_posting\n{settings["prefix"]}stop_posting\nУПРАВЛЕНИЕ ПАБЛИКАМИ РАССЫЛКИ:\n{settings["prefix"]}add_pablic <<id паблика>> <<тип контента(text или image)>>\n{settings["prefix"]}del_pablic <<id паблика>> <<тип контента(text или image)>>\n{settings["prefix"]}show_pablics\nУПРАВЛЕНИЕ ВОЙС БЛАСТИНГОМ\n{settings["prefix"]}start_voice_blasting\n{settings["prefix"]}stop_voice_blasting')


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
    await ctx.reply("На какой канал запустить постинг?", view=testview)


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
    await ctx.reply(f"Постинг прекратился")


@bot.command()
async def start_voice_blasting(ctx):
    if ctx.guild in blastingObj.voice_blast_list:
        await ctx.reply(f"На сервере уже есть войс блатинг")
        return

    blastingObj.voice_blast_list.append(ctx.guild)
    await ctx.reply(f"Начался войс бластинг")
    await blastingObj.voice_blasting(ctx.guild)


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


@bot.command()
async def show_sounds(ctx):
    sound_obj = sounds.Sounds()
    sound_list = sound_obj.get_sounds(ctx.guild)
    if sound_list == 0 or len(sound_list) == 0:
        await ctx.reply('На сервере нет звуков')
        return
    text_message = ''
    for i in range(len(sound_list)):
        text_message += str(i+1) + " " + sound_list[i] + '\n'
    await ctx.reply(text_message)


@bot.command()
async def add_sound(ctx):
    # attachment_message = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.attachments)
    sound_obj = sounds.Sounds()
    if len(ctx.message.attachments) <= 0:
        await ctx.reply('Прикрепи к сообщению с командой файлы')
        return
    response = sound_obj.add_sound(ctx.guild, ctx.message.attachments)
    if len(response) <= 0:
        await ctx.reply('Ни один файл не добавлен.\nФайл должен быть формата mp3')
    else:
        text_message = 'Добавлен(ы):'
        for i in response:
            text_message += '\n' + i
        await ctx.reply(text_message)


@bot.command()
async def del_sound(ctx, name):
    sound_obj = sounds.Sounds()
    response = sound_obj.del_sound(ctx.guild, name)
    text = ''
    match response:
        case 0:
            text = 'Такого звука нет на сервере'
        case 1:
            text = f"{name} удален с сервера"
        case 2:
            text = "Индекс выходит за пределы"

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
