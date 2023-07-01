import discord
from discord.ext import commands
from discord.ext import tasks
import os
from core import Cog_Extension

class Task(Cog_Extension):

    def __init__(self,*args):
        super().__init__(*args)
        #self.peanuts.start()

    '''
    @tasks.loop(seconds=20.0)
    async def peanuts(self):

        await self.bot.wait_until_ready()
        self.channel = self.bot.get_channel(int(os.getenv("general_channel")))
        await self.channel.send("Peanuts !")
    '''

def setup(bot):
    bot.add_cog(Task(bot))