import random
import asyncio
import discord
import vk_api
import logging

from config import vktoken
import pablics
import channel_obj

logger_name = "posting"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
handler1 = logging.FileHandler(f"logs\{logger_name}.log", mode='a')
handler2 = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler1.setFormatter(formatter)
handler2.setFormatter(formatter)
logger.addHandler(handler1)
logger.addHandler(handler2)


class Posting:
    def __init__(self):
        vk_session = vk_api.VkApi(token=vktoken)
        self.session_api = vk_session.get_api()
        self.posting_channels = []
        self.count = 0
        self.pablicsObj = pablics.Pablics()
        # self.pablic_id_text = ["92876084", "202708047"]
        # self.pablic_id_image = ["109290951", "183803447", "198229588", "210666122"]

    async def posting(self, channel: discord.TextChannel, sleep_time=60 * 60 * 2):
        self.posting_channels.append(channel_obj.ChannelObj(channel, self.count))
        temp_count = self.count
        self.count += 1
        logger.info(f'Posting has started at {channel.guild.name}/{channel.name}')
        while True:
            f = False
            for post_obj in self.posting_channels:
                if post_obj.posting_id == temp_count:
                    f = True
                    break
            if not f:
                logger.info(f'Posting has stopped at {channel.guild.name}/{channel.name}')
                return
            text_pablics = self.pablicsObj.get_pablics_id_by_type(channel.guild.id, "text")
            image_pablics = self.pablicsObj.get_pablics_id_by_type(channel.guild.id, "image")
            textpablic = "-" + random.choice(text_pablics)
            imagepablic = "-" + random.choice(image_pablics)
            try:
                poststext = self.session_api.wall.get(owner_id=textpablic, count=100)['items']
                # posts_string = [post['text'] for post in poststext]
                posts_string = []
                for post in poststext:
                    text = post['text']
                    if text != '' and len(post['text']) < 256:
                        posts_string.append(text)

                postsimage = self.session_api.wall.get(owner_id=imagepablic, count=100)['items']
                images = []
                attatcments = [post['attachments'] for post in postsimage]
                for attatchment in attatcments:
                    for obj in attatchment:
                        if obj['type'] == 'photo':
                            images.append(obj['photo']['sizes'][4]['url'])
                            break

                embed = discord.Embed(color=0xff9900, title=str(random.choice(posts_string)))
                embed.set_image(url=random.choice(images))
                await channel.send(embed=embed)
                logger.info(f"Text - {textpablic}\tImage - {imagepablic} has sended at {channel.guild.name}/{channel.name}")
                await asyncio.sleep(sleep_time)
            except Exception as er:
                logger.exception(f"PostingException: Text - {textpablic}\tImage - {imagepablic} at {channel.guild.name}/{channel.name}")

    def del_channel_by_guild_id(self, guild_id: int):
        self.posting_channels = list(filter(lambda x: x.channel.guild.id != guild_id, self.posting_channels))

    def contain_channel(self, channel: discord.TextChannel) -> bool:
        for obj in self.posting_channels:
            if obj.channel == channel:
                return True
        return False

