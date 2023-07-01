
import discord
from discord.ext import commands
import os
from core import Cog_Extension

todolist = []


class TODOLIST_Instruction():
    input_format = ''' first, enter the instuction key word. 
                       Second, enter the time according to the template. 
                       Third, enter the content of todo list'''
    template = "2022/06/13"
    example = "2022/06/13 review history"
            

class TODOlist(Cog_Extension):
    
    @ commands.command()
    async def todo_help(self, ctx):
        await ctx.send(
            "```key word - $add - add new todolist \n```"
            "```         - $delete - delete certain todolist \n```"
            "```         - $delete_all - delete the whole list \n```"
            "```         - $show_all - show the whole list in chronological order \n```"
            
            "```input format: first, enter the instruction key word (end with space) \n```"
            "```            : second, enter the year/month/date (end with space) \n```"
            "```            : third, enter content (press the ENTER to complete) \n```"
        )


    @ commands.command()
    async def add(self, ctx):   #加新的一項
        want_add = ctx.message.content  #取得使用者傳的訊息     
        content = want_add[4:]  #取得使用者要加的訊息
        if len(content) >8:
            if content not in todolist:
             
                todolist.append(content)    #加進 list 
                await ctx.send("you successfully add a todo list")
                
                # except ValueError:
                #     await ctx.send("the format is wrong")
        else:
            await ctx.send("the format is wrong")
        

    @ commands.command()
    async def delete(self, ctx):
        want_delete = ctx.message.content #要刪掉的項目
        content = want_delete[5:]  #取得使用者要刪的訊息
        print(content)
        if content in todolist:
            todolist.remove(content)    #從list 中，移除
            await ctx.send("you successfully delete a todo list")
        else: 
            await ctx.send("there is no todolist that you want to delete")  


    @ commands.command()
    async def delete_all (self, ctx):
        todolist.clear()    #將list 裡面的資料全部刪掉
        await ctx.send("you successfully delete the whole list")        


    @ commands.command()
    async def show_all (self, ctx):
        
        chronological = sorted(todolist)
        
        if len(chronological)>0:
            for i in range(0, len(chronological)): #一個一個印出來
                if i == 0:
                    await ctx.send(f"Your todo list!! \n {i+1}: {chronological[i]} \n")
                elif i>0 and i < len(todolist)-1:
                    await ctx.send(f"{i+1}: {chronological[i]} \n")
                else:
                    await ctx.send(f"{i+1}: {chronological[i]} ")
        else: 
            await ctx.send("There is nothing in the todolist")


def setup(bot):
    bot.add_cog(TODOlist(bot))