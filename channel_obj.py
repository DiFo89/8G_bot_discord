import discord


class ChannelObj:

    def __init__(self, channel: discord.TextChannel, posting_id: int):
        self.channel = channel
        self.posting_id = posting_id
