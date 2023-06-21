import discord
import asyncio
import random
import os
import logging
from os import walk
from mutagen.mp3 import MP3

logger_name = "voice_blast"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
handler1 = logging.FileHandler(f"logs\{logger_name}.log", mode='a')
handler2 = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler1.setFormatter(formatter)
handler2.setFormatter(formatter)
logger.addHandler(handler1)
logger.addHandler(handler2)


class VoiceBlast:
    def __init__(self):
        self.voice_blast_list = []

    def _get_sounds(self, path):
        sounds = []
        for (dirpath, dirnames, filenames) in walk(path):
            sounds.extend(filenames)
            break
        for sound in sounds:
            if sound.split(".")[1] != "mp3":
                sounds.remove(sound)
        return sounds

    async def voice_blasting(self, guild: discord.Guild):
        logger.info(f"Voice blasting has started at {guild.name} ({guild.id})")
        while True:

            #await asyncio.sleep(random.randint(2000, 10000))
            await asyncio.sleep(random.randint(60, 240))
            if guild not in self.voice_blast_list:

                logger.info(f'Voice blasting has stopped at {guild.name} ({guild.id})')
                return

            vc_channels = guild.voice_channels
            channel_list = []
            for vc in vc_channels:
                if len(vc.members) > 0:
                    channel_list.append(vc)
            if len(channel_list) > 0:
                try:
                    path_file = os.path.dirname(__file__)
                    path = os.path.join(path_file, "sounds", str(guild.id))
                    if not os.path.exists(path):
                        path = os.path.join(path_file, "sounds")
                    sounds = self._get_sounds(path)
                    if len(sounds) == 0:
                        path = os.path.join(path_file, "sounds", "standart")
                        sounds = self._get_sounds(path)

                    sound = random.choice(sounds)
                    path = os.path.join(path, sound)
                    duration = MP3(path).info.length

                    channel = random.choice(channel_list)
                    voice = await channel.connect()
                    voice.play(discord.FFmpegPCMAudio(source=path))

                    logger.info(f"{sound} has played at {guild.name} ({guild.id})")
                    max_time = 60
                    if duration > max_time:
                        await asyncio.sleep(max_time)
                    else:
                        await asyncio.sleep(duration + 0.5)
                    await voice.disconnect()
                except Exception as er:
                    logger.exception(f"VoiceBlastError: sound - \"{sound}\", server - \"{guild.name}\"")

