import time
import requests
from bs4 import BeautifulSoup as Blp
import discord
from discord.ext import commands
import os
from core import Cog_Extension

url = "https://udn.com/news/index"
content = requests.get(url)
link_new = []
link_hot = []
link_keywords = []
doc = Blp(content.text,"html.parser")
news_time = doc.find_all("span",{"class" : "tab-link__note"})
news_title = doc.find_all("span",{"class" : "tab-link__title"})
context_box__content = doc.find_all('div',{"class":"context-box__content"})
context_new__as = context_box__content[0].find_all('a')
a_keywords = doc.find_all("a",{"class" : "btn btn-border btn-border--blue btn-keyword"})

for a in context_new__as:
    link_new.append(a.get('href'))
context_hot__as = context_box__content[1].find_all('a')

for a in context_hot__as:
    link_hot.append(a.get('href'))

for l in a_keywords:
    link_keywords.append(l.get('href'))

class News(Cog_Extension):
    
    @commands.command()
    async def BreakingNews(self, ctx):
        embed=discord.Embed(title="新聞", description="即時新聞", color=0x0281f7)
        embed.set_author(name="聯合新聞網")
        for i in range(9):
            embed.add_field(name=f'時間:{news_time[i].string}  標題:{news_title[i].string}', value=f'完整新聞連結:{link_new[i]}', inline=True)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def HotNews(self, ctx):
        embed=discord.Embed(title="新聞", description="熱門新聞", color=0xf20707)
        embed.set_author(name="聯合新聞網")
        for i in range(9,18):
            embed.add_field(name=f'新聞編號:{news_time[i].string}  標題:{news_title[i].string}', value=f'完整新聞連結:{link_hot[i-9]}', inline=True)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def NewsKeyWords(self, ctx):
        embed=discord.Embed(title="新聞", description="關鍵字", color=0x8c07f2)
        embed.set_author(name="聯合新聞網")
        for i in range(len(a_keywords)):
            embed.add_field(name=f'關鍵字:{a_keywords[i].text}', value=f'完整新聞連結:{link_keywords[i]}', inline=True)
        await ctx.send(embed=embed)
    
def setup(bot):
    bot.add_cog(News(bot))