import discord
import asyncio
import random
import os
from os import walk
from mutagen.mp3 import MP3

# pathfile = os.path.dirname(__file__)
# path = os.path.join(pathfile, "sounds", "Tactical Nuke.mp3")


class VoiceBlast:
    def __init__(self):
        self.voice_blast_list = []

    async def voice_blasting(self, guild):
        while True:

            await asyncio.sleep(random.randint(1000, 6000))

            if guild not in self.voice_blast_list:
                print(f'At {guild.name} voice blacsting has stopped')
                return

            vc_channels = guild.voice_channels
            channel_list = []
            for vc in vc_channels:
                if len(vc.members) > 0:
                    channel_list.append(vc)
            if len(channel_list) > 0:
                try:
                    path_file = os.path.dirname(__file__)
                    path = os.path.join(path_file, "sounds")
                    sounds = []
                    for (dirpath, dirnames, filenames) in walk(path):
                        sounds.extend(filenames)
                        break
                    for sound in sounds:
                        if sound.split(".")[1] != "mp3":
                            sounds.remove(sound)

                    sound = random.choice(sounds)
                    path = os.path.join(path_file, "sounds", sound)
                    duration = MP3(path).info.length

                    channel = random.choice(channel_list)
                    voice = await channel.connect()
                    voice.play(discord.FFmpegPCMAudio(source=path))
                    if duration > 30:
                        await asyncio.sleep(30)
                    else:
                        await asyncio.sleep(duration + 1)
                    await voice.disconnect()
                except Exception as er:
                    print('Error: ', er)

