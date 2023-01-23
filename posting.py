import random
import asyncio
import discord
import vk_api
import json

from config import vktoken
import pablics

pablicsObj = pablics.Pablics()


class Posting:
    def __init__(self):
        vk_session = vk_api.VkApi(token=vktoken)
        self.session_api = vk_session.get_api()
        self.posting_channels = []
        # self.pablic_id_text = ["92876084", "202708047"]
        # self.pablic_id_image = ["109290951", "183803447", "198229588", "210666122"]

    async def posting(self, channel):
        while True:
            text_pablics = pablicsObj.get_pablics_id_by_type(channel.guild.id, "text")
            image_pablics = pablicsObj.get_pablics_id_by_type(channel.guild.id, "image")
            # textpablic = "-" + random.choice(self.pablic_id_text)
            textpablic = "-" + random.choice(text_pablics)
            # imagepablic = "-" + random.choice(self.pablic_id_image)
            imagepablic = "-" + random.choice(image_pablics)
            if channel not in self.posting_channels:
                print(f'At {channel.guild}/{channel.name} posting has stopped')
                break
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
                print(f'text: {textpablic}\timage: {imagepablic} has sended')
                await asyncio.sleep(60 * 60 * 2)

            except Exception as er:
                print(er)