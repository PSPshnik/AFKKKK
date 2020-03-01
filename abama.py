from .. import loader, utils

import logging
import datetime
import time

logger = logging.getLogger(__name__)


def register(cb):
    cb(AFKMod())


@loader.tds
class AFKMod(loader.Module):
    """Provides a message saying that you are unavailable"""
    strings = {"name": "АФК",
               "gone": "<b>Я пиздую АФКишить</b>",
               "back": "<b>Здарова, ряботяги!</b>",
               "afk": "<b>Я в АФК, погоди (since {} ago).</b>",
               "afk_reason": "<b>Прямо сейчас я в АФК (since {} ago).\nReason:</b> <i>{}</i>",
               "fuck": "FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUCK"}

    def config_complete(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self._db = db
        self._me = await client.get_me()

    async def афкcmd(self, message):
        """.afk [message]"""
        if utils.get_args_raw(message):
            self._db.set(__name__, "afk", utils.get_args_raw(message))
        else:
            self._db.set(__name__, "afk", True)
        self._db.set(__name__, "gone", time.time())
        self._db.set(__name__, "ratelimit", [])
        await self.allmodules.log("afk", data=utils.get_args_raw(message) or None)
        await utils.answer(message, self.strings["gone"])
    
    
    async def waitcmd(self, message):
        time.sleep(5)
        await utils.answer(message, "Через 5 секунд это удалится")
        await message.delete()
    
    
    async def afkcmd(self, message):
        """.afk [message]"""
        if utils.get_args_raw(message):
            self._db.set(__name__, "afk", utils.get_args_raw(message))
        else:
            self._db.set(__name__, "afk", True)
        self._db.set(__name__, "gone", time.time())
        self._db.set(__name__, "ratelimit", [])
        await self.allmodules.log("afk", data=utils.get_args_raw(message) or None)
        await utils.answer(message, self.strings["gone"])

    async def fuckcmd(self, message):
        await utils.answer(message, self.strings["fuck"])

    async def анафкcmd(self, message):
        """Remove the AFK status"""
        self._db.set(__name__, "afk", False)
        self._db.set(__name__, "gone", None)
        self._db.set(__name__, "ratelimit", [])
        await self.allmodules.log("unafkkkk")
        await utils.answer(message, self.strings["back"])

    async def unafkcmd(self, message):
        """Remove the AFK status"""
        self._db.set(__name__, "afk", False)
        self._db.set(__name__, "gone", None)
        self._db.set(__name__, "ratelimit", [])
        await self.allmodules.log("unafkkkk")
        await utils.answer(message, self.strings["back"])

    async def watcher(self, message):
        if message.mentioned or getattr(message.to_id, "user_id", None) == self._me.id:
            logger.debug("tagged!")
            ratelimit = self._db.get(__name__, "ratelimit", [])
            if utils.get_chat_id(message) in ratelimit:
                return
            else:
                self._db.setdefault(__name__, {}).setdefault("ratelimit", []).append(utils.get_chat_id(message))
                self._db.save()
            user = await utils.get_user(message)
            if user.is_self or user.bot or user.verified:
                logger.debug("User is self, bot or verified.")
                return
            if self.get_afk() is False:
                return
            now = datetime.datetime.now().replace(microsecond=0)
            gone = datetime.datetime.fromtimestamp(self._db.get(__name__, "gone")).replace(microsecond=0)
            diff = now - gone
            if self.get_afk() is True:
                ret = self.strings["afk"].format(diff)
            elif self.get_afk() is not False:
                ret = self.strings["afk_reason"].format(diff, self.get_afk())
            await utils.answer(message, ret)

    def get_afk(self):
        return self._db.get(__name__, "afk", False)
