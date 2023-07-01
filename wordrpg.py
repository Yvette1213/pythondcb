
from abc import ABC, abstractclassmethod
import json
from dataclasses import dataclass
from discord.ext import commands
from click import UsageError, pass_context
from core import Cog_Extension
import discord
import asyncio
import numpy as np
import os
import random


@dataclass
class Game_think_message():
    error = '指令錯誤，使用『`$GT ?`』或是『`$GT help`』可以查詢使用方法。'
    quit = '現在已經退出此局遊戲！'
    not_in_game = '你現在並不是在遊戲中的玩家，使用『`$GT ?`』或是『`$GT help`』可以查詢遊玩方法'
    in_game = '你已經在遊戲中，如需退出使用『`$GT quit`』即可'
    join = '成功加入遊戲，使用『`$GT ?`』或是『`$GT help`』可以查詢使用方法。'
    usage = '使用『`$GT join`』可以加入遊戲\n在遊戲中可以互動的會顯示`[名稱]`這樣的黑框字體，使用『`$GT 互動 [名稱]`』來與空間或是物品互動，需返回請在使用一次互動。\n在不同空間使用『`$GT 交換`』將當前空間與手上的東西做交換(空的也能換)，遊戲中玩家的背包空間只有雙手，會經常交換物品所以請詳記物品位置。\n『`$GT 物品`』可以看到當前可以拿、手上的物品。『`$GT 周圍`』能環顧周圍的環境。\n如在遊戲中需退出使用『`$GT quit`』即可不保存退出遊戲。'


class Game_space():
    def __init__(self, name:str, prompt_text:str, *, item:list = list(), access_denied_text:str = "can't interact", entry_pass_item:list = list()) ->None:
        self.name = name
        self.prompt_text = prompt_text
        self.item = item
        self.access_denied_text = access_denied_text
        self.entry_pass_item = entry_pass_item
        self.connect = dict()

    def item_exchange(self, items:list) ->str:
        if not(self.item or items):
            report = "nothing happen"
            return report
        report = f'you have: {items}\n{self.name}: {self.item}\n\t\t\t:arrow_down:\n you have {self.item}\n{self.name}:{items}'
        self.item[:], items[:] = items[:], self.item[:]
        return report

    def add_connect(self, name:str, destination) -> None:
        self.connect[name] = destination

    def what_connect_to(self) -> list:
        """將有連接的地方串接成字串並回傳"""
        return list(self.connect.keys())  # 連接到的清單

    def what_takebel(self) -> list:
        return self.item  # 內部存放的物品


def connect_space(A: Gmae_space, /, *B: Gmae_space) -> None:
    """將單個A雙向接上B，可以用多個輸入"""
    for B_one in B:
        A.add_connect(B_one.name, B_one)  # 前往空間
        B_one.add_connect(A.name, A)  # 返回上個空間


def create_map():  # -> dict:
    """創建一張遊戲地圖"""
    Map = {
        "__init__": Gmae_space("__init__", "初始化區域"),
        "玄關": Gmae_space("玄關", "你進入到了玄關，旁邊還有`鞋櫃`、`雨傘桶`，背後有`大門`前方是一條`走廊`"),
        "鞋櫃": Gmae_space("鞋櫃", "你蹲下查看了鞋櫃，裡面有著一雙`鞋子`可以拿。返回：`玄關`", item=["兩隻皮鞋", "鞋油", "蚊香"]),
        "雨傘桶": Gmae_space("雨傘桶", "你走到旁邊查看了傘桶，裡面是空的。返回：`玄關`"),
        "大門": Gmae_space("大門", "你用手上的鑰匙打開了大門並走了出去，你茫然的看著外面的景色，前面就是`自由`你不知道該怎麼辦。返回：`屋子`", entry_pass_item=["大門鑰匙"], access_denied_text="你嘗試轉動門把，但你很不解為什麼會被反鎖在這間屋子裡面，看來需要拿`大門鑰匙`來解鎖。"),
        "走廊": Gmae_space("走廊", "木質地板的走廊，兩側有`臥室`、`廁所`、`廚房`、`客廳`。返回：`玄關`", item=["被揉成團的照片"]),

        "臥室": Gmae_space("臥室", "這裡是狹小的休息空間也是工作空間，中間正對門口有一張單人床上面有印花圖案，右側有`衣櫃`，床左側有`茶几`就放在灰色地毯的上方。返回：`走廊`"),
        "衣櫃": Gmae_space("衣櫃", "裡面只有一件小孩子的衣服，不知道什麼原因你在這件衣物上感到一絲熟悉，裡面擺著一個突兀的`保險箱`。返回：`臥室`"),
        "保險箱": Gmae_space("保險箱", "你轉動按照紙條密碼，打開了保險箱，裡面只有放著一把`大門鑰匙`，其他什麼都沒有。你感覺很奇怪，為什麼大門鑰匙需要被這樣子的鎖起來。返回；`臥室`", access_denied_text="你嘗試亂轉密碼，但是怎麼都打不開，或許需要某個知道密碼的人才能開啟吧。", entry_pass_item=["被壓著的密碼紙條"], item=["大門鑰匙"]),
        "茶几": Gmae_space("茶几", "上面擺著一些文件，看起來是關於會計相關工作，旁邊擺著一個筆筒與水杯，桌子地下散落著一些能量飲料的空瓶罐，看這著些連你都感受到一絲的疲憊。返回：`臥室`"),

        "廁所": Gmae_space("廁所", "正常來說無法進入這裡", entry_pass_item=["None"], access_denied_text="當打算去開廁所門的瞬間感受到頭暈噁心，甚至出現破裂聲、飛機、刺耳的幻聽，讓你打消了開門的想法。"),

        "廚房": Gmae_space("廚房", "廚房，桌沿放了些頗具情調的小蠟燭及一些醬料瓶，四張`椅子`但永遠都多一張，旁邊是冰箱與洗碗槽，上方有些櫥櫃，底下有洗碗機，窗戶框上還擺著一個花瓶，上頭的百合花開的美麗，`花盆`的碟子裡還有些許的水。返回：`走廊`"),
        "花盆": Gmae_space("花盆", "你走進看著這朵花，舒緩了一些壓力，真是被留下的美麗，如果是想找一個休息的地方，百合花田最適躺在裏頭避風避雨了。返回：`廚房`", item=["被壓著的密碼紙條"]),
        "椅子": Gmae_space("椅子", "拉開了椅子座了上去，看著窗外的風景好像很不錯，不知道這樣的愜意還可以停留久呢？返回：`廚房`"),

        "客廳": Gmae_space("客廳", "裡面的東西早已被裝箱打包，看來是準備要搬家了，或許是要準備展開新的生活。返回：`走廊`", item=["雜物箱", "包了氣泡紙的花瓶", "藍綠色膠帶", "半透明塑膠布"]),

        "外面": Gmae_space("自由", "你稍加思索過後還是決定走了出去，外頭的鳥兒、落葉、風、一切會動的東西如同時間暫停似的不再移動。都還沒回過神來，卻開始飄了起來，你在逐漸的變輕盈，周圍變得越來越亮也越來越渺小，沒有慌張反而有種奇異的放鬆。雖然不知道會通往什麼地方但也只能繼續`前進`。"),
        "外面前進": Gmae_space("前進", "或許是周圍太亮了，又或許是消失了，你開始逐漸看不到自己的輪廓，但也不再計較這些，你在此時才回想起來發生了些什麼。\n工作的時候總是必須到很晚才能回到家裡，也沒有時間陪伴她，只有編輯報表以及更多的瑣事，也知道這樣下去遲早有一天會成為問題，為了那該死的薪水，為了家人的生活，不得不再繼續撐下去。難得的假日就想要好好陪伴一下，於是買了各種道具就準備好好的去遊玩一下。到了溪邊那裡，水很涼爽、太陽也很溫暖因該會是一次很好的回憶。\n過了午後開始下起小雨，起初也沒多少注意，就換到岸邊繼續幫忙烤肉。再大家都吃飽之後，就在遮陽傘下聊天，卻沒有人注意到溪水不知何時已經沒有再流下來。\n到這裡記憶就伴隨著沖刷下來的泥流斷在了那個瞬間，如果平常有珍惜就好了...\n\n`以上內容純屬虛構，如有雷同純屬巧合`\n【感謝遊玩 Seize the day】"),

        "回去屋子": Gmae_space("屋子", "在門口又想了半天，總覺得不太對勁，於是又折返了回去，走到了廚房，那模糊的記憶裡傳來的聲音讓你有點暈眩，於是你座在了面對窗戶的椅子上，看著窗框旁的花朵來緩解不舒服得感覺，好像也沒那的不適了，也看著窗外的景色，一邊在思考究竟這裡發生了什麼事情，為什麼我會被困在這裡，就這樣看這的話我可以做些什麼事情等等的，就這樣思考...思考...\n也不知道過了多久，房間的布局也改變了，花早已凋零丟棄，但窗外的景色永遠，永遠的定格在那裡，永遠也不回離開，永遠也不再流逝...\n\n`以上內容純屬虛構，如有雷同純屬巧合`\n【感謝遊玩 Seize the day】"),
    }
    """把創建好的遊戲地圖連結起來"""
    Map["__init__"].add_connect("__entry__", Map["玄關"])  # 進入點接至__entry__(玄關)
    connect_space(Map["玄關"], Map["鞋櫃"], Map["雨傘桶"], Map["大門"], Map["走廊"])

    connect_space(Map["走廊"], Map["臥室"], Map["廁所"], Map["廚房"], Map["客廳"])

    connect_space(Map["臥室"], Map["衣櫃"], Map["茶几"])
    Map["衣櫃"].add_connect(Map["保險箱"].name, Map["保險箱"])
    Map["保險箱"].add_connect(Map["臥室"].name, Map["臥室"])

    connect_space(Map["廚房"], Map["椅子"], Map["花盆"])

    Map["大門"].add_connect(Map["回去屋子"].name, Map["回去屋子"])

    Map["大門"].add_connect(Map["外面"].name, Map["外面"])
    Map["外面"].add_connect(Map["外面前進"].name, Map["外面前進"])

    return list(Map.values())  # 將地圖打包並回傳


class Player():
    Map: dict[str:Gmae_space]
    items: list
    location: Gmae_space

    def __init__(self) -> None:
        self.Map = create_map()  # 創建地圖
        self.location = self.Map[0]  # __init__
        self.items = list()  # 初始化玩家物品

    def item_exchange(self) -> str:
        return self.location.item_exchange(self.items)  # 交換

    def can_entry(self, destination: Gmae_space) -> bool:
        """檢測空間是否可以進入"""
        if destination.entry_pass_item:  # 此空間需要物品才能進入
            return self.items == destination.entry_pass_item  # 手上 == 通過需要的物品
        return True  # 不需要物品就可以通過

    def move_in_to(self, destination_name: str) -> str:
        """嘗試移動，回傳嘗試的報告(str)"""
        destination = self.location.connect.get(destination_name)  # 取得目的地
        if not destination:  # 沒有這個空間
            return f"`{destination_name}`並不存在，請輸入有效的`[名稱]`"
        if not self.can_entry(destination):  # 此空間沒辦法進入
            return destination.access_denied_text  # 回傳進入失敗訊息

        self.location = destination  # 將玩家位置設定為目的地(移動)
        return self.location.prompt_text

    def show_items(self) -> str:
        can_take = self.location.what_takebel()
        hold = self.items
        if bool(can_take) or bool(hold):
            return f"你手上持有的：{hold}   交換當前可以拿{can_take}"
        return "你嘗試尋找能換的東西，什麼事情都沒有發生。"

    def show_space(self) -> str:
        return f"目前這個地方有：{self.location.what_connect_to()}"


class Game_think_GM():
    playing: dict[int:Player]

    def __init__(self) -> None:
        self.playing = dict()

    def quit(self, playerID: int) -> None:
        """退出遊戲"""
        del self.playing[playerID]  # 清除遊戲

    def InGame(self, playerID: int) -> bool:
        """檢查玩家是否在遊戲內"""
        return playerID in self.playing

    def join(self, playerID: int):
        """創建並加入玩家資訊"""
        player = Player()  # 創建
        self.playing[playerID] = player
        return player.move_in_to("__entry__")  # 初始化位置

    def loging(self, playerID: int) -> Player:
        """用ID取得玩家在遊戲裡的資料，如果每有就初始化"""
        return self.playing[playerID]  # 回傳資訊


class Main(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.Game = Game_think_GM()

    @ commands.command()
    async def GT(self, ctx):
        """使用『`$GT ?`』或是『`$GT help`』可以查詢使用方法"""
        # 去除前方必定內容以及轉換list (_, contents = $abGame ???)
        playerID = ctx.author.id
        _, *contents = str(ctx.message.content).split(' ')
        match contents:
            case ['join'] if self.Game.InGame(playerID):
                await ctx.send(Game_think_message.in_game)  # 傳送訊息告知已經在遊戲中了
            case ['join']:   # TODO加入
                await ctx.send(Game_think_message.join)  # 傳送訊息告成功加入遊戲
                await ctx.send(self.Game.join(playerID))
            case ['quit' | 'exit'] if self.Game.InGame(playerID):  # 玩家有在遊戲內的退出
                self.Game.quit(playerID)  # 退出此玩家
                await ctx.send(Game_think_message.quit)  # 傳送訊息告已經退出成功了
            case ['quit' | 'exit']:   # 玩家沒有在遊戲內卻要退出
                await ctx.send(Game_think_message.not_in_game)  # 傳送訊息告知不在遊戲中
            case ["help" | "?"]:  # 怎麼用
                await ctx.send(Game_think_message.usage)  # 發送用法
            case [*_]:  # 沒觸發指令的全接住
                await self._GT_game_round(ctx, playerID, contents)  # 進入遊戲流程

    async def _GT_game_round(self, ctx, playerID: int, contents) -> None:
        """以下為遊戲部分"""
        if not self.Game.InGame(playerID):  # 當進入遊戲流程但玩家並沒有加入遊戲
            await ctx.send(Game_think_message.not_in_game)  # 傳送訊息告知不在遊戲中
            return  # 用於中斷程式的回傳

        player = self.Game.loging(playerID)  # 取得單個玩家
        report = ""
        match contents:
            case ["交換"]:
                report = player.item_exchange()  # 與目前空間的物品交換並取得回報
            case ["互動", content]:
                report = player.move_in_to(content)  # 移動並取得回報
            case ["周圍"]:
                report = player.show_space()
            case ["物品"]:
                report = player.show_items()
            case [*_]:
                report = Game_think_message.error   # 接住所有例外
        if report:  # 如果有需要發送的東西
            await ctx.send(report)  # 傳送訊息告知回報情況


def setup(bot) -> None:
    bot.add_cog(Main(bot))
