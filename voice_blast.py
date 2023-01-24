import discord
import asyncio
import random
import os

pathfile = os.path.dirname(__file__)
path = os.path.join(pathfile, "sounds", "Tactical Nuke.mp3")


class VoiceBlast:
    def __init__(self):
        self.voice_blast_list = []

    async def voice_blasting(self, guild):
        '''vc_channels = guild.voice_channels
        channel_list = []
        for vc in vc_channels:
            if len(vc.members) > 0:
                channel_list.append(vc)
        if len(channel_list) > 0:
            pathfile = os.path.dirname(__file__)
            path = os.path.join(pathfile, "sounds", "Tactical Nuke.mp3")
            channel = random.choice(channel_list)
            try:
                voice = await channel.connect()
                voice.play(discord.FFmpegPCMAudio(source=path))
                await asyncio.sleep(15)
                await voice.disconnect()
            except Exception as er:
                print('Error: ', er)'''
        while True:
            await asyncio.sleep(random.randint(1000, 6600))

            if guild not in self.voice_blast_list:
                print(f'At {guild.name} voice blacsting has stopped')
                return
            vc_channels = guild.voice_channels
            channel_list = []
            for vc in vc_channels:
                if len(vc.members) > 0:
                    channel_list.append(vc)
            if len(channel_list) > 0:
                pathfile = os.path.dirname(__file__)
                path = os.path.join(pathfile, "sounds", "fnaf-1-music-box.mp3")
                channel = random.choice(channel_list)
                try:
                    voice = await channel.connect()
                    voice.play(discord.FFmpegPCMAudio(source=path))
                    await asyncio.sleep(15)
                    await voice.disconnect()
                except Exception as er:
                    print('Error: ', er)

