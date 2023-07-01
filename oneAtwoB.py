
from dataclasses import dataclass
from discord.ext import commands
from click import pass_context
from core import Cog_Extension
import discord
import asyncio
import numpy as np
import os
import random


"""
舊方法如下：O(n^2)
先比最高位數字，如果相等A+=1，不相等就看猜的數字在答案內就B+=1，之後就往n-1位數字搜尋直到結束。
""""""
新方法如下：O(n)
答案 = 把隨機抽出來的數字當作index找到在[None]*10的list裡的位置改寫為此數字在答案中的index，
猜的時候A,B = 猜的數字當作index從list取值，如果相等就是A+=1就contnue，再來得到不是None就為B+=1
此方法使用於現在遊戲的規模加速效果有限，但當猜測數字更龐大就會有更好的效果。(內容在程式碼63、72行)
升級日期：2022/06/25
"""


@dataclass
class AB_Game_message():
    error = '指令錯誤，使用『`$abGame ?`』或是『`$abGame help`』可以查詢使用方法。'
    quit = '現在已經退出此局遊戲！'
    not_in_game = '你現在並不是在遊戲中的玩家，使用『`$abGame ?`』或是『`$abGame help`』可以查詢遊玩方法'
    correct_answer = '恭喜您猜中正確數字。你可以使用『`$abGame ranking`』來查看排行榜。'
    new_game = '已建立一局新的遊戲！'
    usage = '使用『`$abGame + 1～9四位不重複整數`』中間以空隔開即可進行遊戲。\n使用『`$abGame quit`』中間以空隔開即可停止本遊戲，並公布答案(不登記於排行榜)。\n使用『`$abGame ranking`』來查看排行榜。'


class Clearances_Number():
    def __init__(self) -> None:
        self.Score_bar = dict()

    def add(self, player_name: str) -> None:
        # 使用名子作為記分板key並且加分
        self.Score_bar[player_name] = self.Score_bar.get(player_name, 0) + 1

    def get_top_10(self) -> str:
        items = self.Score_bar.items()  # 玩家ID對應到分數的dict
        top_10 = sorted(items, key=lambda x: x[1], reverse=True)[:10]
        output_str = '```分數\t\t\t名子...'
        for name, Number in top_10:
            # 只取名子前10個字
            output_str += f'\n{Number}\t\t\t{name[:10]}'
            if len(name) > 10:  # 名子過長替換為...
                output_str += '...'
        return output_str + '```'  # 關閉黑框


class AB_Game():
    def __init__(self) -> None:
        self.playing = dict()

    def input_legal(self, content) -> bool:
        return (content.isdigit() and  # 純數字
                len(content) == 4 and  # 長度
                not(max([content.count(i) > 1 for i in content])))  # 沒有重複數字

    def generate_answer(self) -> list[int]:
        answer = [-1]*10
        random_answer = random.sample(range(1, 10), 4)
        index = 0
        for number in random_answer:
            answer[number] = index  # 把答案指向他的位置
            index += 1
        return answer

    def guess(self, guess: str, playerID: int):
        A = B = index = 0
        answer = self.playing[playerID]
        for number in map(int, guess):
            answer_index = answer[number]
            if answer_index == index:  # 猜的數字指向位置相同
                A += 1  # 猜對+1
            elif answer_index != -1:  # 有猜中數字但指向的位置不對
                B += 1  # 錯位+1
            index += 1  # 下面一位
        return A, B

    def InGame(self, playerID: int) -> bool:
        return playerID in self.playing

    def join(self, playerID: int) -> None:
        # 用id儲存答案
        self.playing[playerID] = self.generate_answer()

    def quit(self, playerID: int) -> None:
        del self.playing[playerID]  # 清除遊戲


class Main(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.Clearances_Number = Clearances_Number()
        self.Game = AB_Game()

    @ commands.command()
    async def abGame(self, ctx):
        """使用『`$abGame ?`』或是『`$abGame help`』可以查詢使用方法"""
        # 去除前方必定內容以及轉換list (_, contents = $abGame ???)
        playerID = ctx.author.id
        _, *contents = str(ctx.message.content).split(' ')
        match contents:
            case ["help" | "?"]:  # 怎麼用
                await ctx.send(AB_Game_message.usage)
            case ["ranking"]:  # 排行榜
                await ctx.send(self.Clearances_Number.get_top_10())
            case ['quit' | 'exit']:  # 退出
                if self.Game.InGame(playerID):
                    self.Game.quit(playerID)
                    await ctx.send(AB_Game_message.quit)
                else:
                    await ctx.send(AB_Game_message.not_in_game)
            case [_]:
                if not self.Game.input_legal(contents[-1]):  # 輸入不合法
                    await ctx.send(AB_Game_message.error)  # 不合法，報錯
                    return
                if not self.Game.InGame(playerID):
                    self.Game.join(playerID)  # 如果玩家不在遊戲裡就創建一局遊戲
                    await ctx.send(AB_Game_message.new_game)  # 告訴玩家遊戲已經開始
                A, B = self.Game.guess(contents[-1], playerID)  # 進行猜測
                if A != 4:  # 沒猜對
                    await ctx.send(f'猜 `{contents[-1]!r}` 得到了 {A}A {B}B ')
                    return
                player_display_name = ctx.message.author.display_name  # 獲得玩家顯示的名稱
                await ctx.send(f'猜 `{contents[-1]!r}` {AB_Game_message.correct_answer}')
                await ctx.message.delete()  # 刪除玩家發出的訊息(讓畫面簡潔)
                self.Game.quit(playerID)
                self.Clearances_Number.add(player_display_name)


def setup(bot):
    bot.add_cog(Main(bot))