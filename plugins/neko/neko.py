# encoding:utf-8
import requests

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *


@plugins.register(
    name="Neko",
    desire_priority=-1,
    hidden=False,
    desc="generate neko",
    version="1.0",
    author="Only(AR)",
)
class Neko(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Neko] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT
        ]:
            return

        if e_context["context"].type == ContextType.TEXT:
            content = e_context["context"].content
            if content.startswith("$"):
                cmds = content[1:].split()
                if len(cmds) == 1 and cmds[0] == "neko":
                    reply = Reply(ReplyType.IMAGE_URL, self.get_img_url("https://nekos.best/api/v2/neko"))
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
                    return

    def get_help_text(self, **kwargs):
        help_text = "$neko: 获取猫娘图片喵~"
        return help_text

    def get_img_url(self, url):
        response = requests.get(url)
        result = response.json()
        return result["results"][0]["url"]
