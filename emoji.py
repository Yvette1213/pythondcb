import requests
import json
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
import os
from core import Cog_Extension
import random
import cmds.emoji as emoji
import numpy as np
class bullshit(Cog_Extension):
    @commands.command()
    async def bullshitMaker(self, ctx):
        url = "https://api.howtobullshit.me/bullshit"
        want = ctx.message.content
        input = want.split()
        Topic = input[1]
        length = input[2]
        post_params = {'Topic': Topic, 'MinLen':int(length)}
        post = json.dumps(post_params)
        response = requests.post(url, data = post)
        soup = BeautifulSoup(response.text, "html.parser")
        await ctx.send(str(soup))
    @commands.Cog.listener()
    async def on_message(self, msg):
        number_random = random.randint(0,9)
        number_random_1 = random.randint(0,3)
        say_hello = ["你好","有事嗎","幹嘛"]
        List = ["哈囉","嗨嗨","在嗎","嘿"]
        for i in List:
            if msg.content.find(i) >= 0 and msg.author != self.bot.user:
                await msg.channel.send(say_hello[number_random_1])
        List_start = ["我跟你說","欸欸","那個"]
        perfunctory_1 = ["喔是喔","笑死","那確實","雀食","對對對","好喔","哈哈","哦~~哈哈真有趣","謝謝您欸~笑爛","酷喔。"]
        for i in List_start:
            if msg.content.find(i) >= 0 and msg.author != self.bot.user:
                await msg.channel.send(perfunctory_1[number_random])
    @commands.command()
    async def RandomEmoji(self, ctx):
        list_random_number = []
        emoji_list = ["\U0001F600","\U0001F603","\U0001F604","\U0001F601","\U0001F606","\U0001F605","\U0001F923","\U0001F602","\U0001F642","\U0001F643",
             "\U0001F609","\U0001F60A","\U0001F607","\U0001F970","\U0001F60D","\U0001F929","\U0001F618","\U0001F617","\U0001F61A",
             "\U0001F619","\U0001F60B","\U0001F61B","\U0001F61C","\U0001F92A","\U0001F61D","\U0001F911","\U0001F917","\U0001F92D","\U0001F92B",
             "\U0001F914","\U0001F910","\U0001F928","\U0001F610","\U0001F611","\U0001F636","\U0001F60F","\U0001F612","\U0001F644","\U0001F62C",
             "\U0001F925","\U0001F60C","\U0001F614","\U0001F62A","\U0001F924","\U0001F634","\U0001F637","\U0001F912","\U0001F915","\U0001F922"]
        def choiceNum():
            number_random = random.randint(0,len(emoji_list)-1)
            list_random_number.append(number_random)
        for i in range(3):
            choiceNum()
        await ctx.send(emoji_list[list_random_number[0]]+emoji_list[list_random_number[1]]+emoji_list[list_random_number[2]])
        
def setup(bot):
    bot.add_cog(bullshit(bot))