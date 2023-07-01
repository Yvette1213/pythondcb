import discord
from discord.ext import commands
import os
from core import Cog_Extension

class Event(Cog_Extension):

    @commands.Cog.listener()
    async def on_member_join(self, member):
        g_channel = self.bot.get_channel(int(os.getenv("general_channel")))
        await g_channel.send(f"歡迎{member}加入!")


    @commands.Cog.listener()
    async def on_message(self, msg):
        List = ["Never","gonna","give","up"]
        for i in List:
            if msg.content.find(i) >= 0 and msg.author != self.bot.user:
                await msg.channel.send('Never gonna give u up !')

def setup(bot):
    bot.add_cog(Event(bot))