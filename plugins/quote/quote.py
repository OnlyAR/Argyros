# @File Name:     quote
# @Author :       Jun
# @date:          2023/6/25
# @Description :
import os

import requests

import plugins
from bridge.context import ContextType
from common.log import logger
from plugins import Plugin, Event, EventContext, EventAction


@plugins.register(
    name="Quote",
    desire_priority=0,
    hidden=False,
    desc="引用名人名言",
    version="1.0",
    author="Only(AR)",
)
class Quote(Plugin):
    def __init__(self):
        super().__init__()
        try:
            curdir = os.path.dirname(__file__)
            prompt_path = os.path.join(curdir, "prompt.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.prompt = f.read()
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[quote] inited")
        except Exception as e:
            logger.warn("[quote] init failed")
            logger.warn(e)
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
        ]:
            return
        content = e_context["context"].content.strip()

        if content.startswith("$") and content[1:].strip() == "quote":
            e_context["context"].content = self.prompt.format(get_quote())
            e_context.action = EventAction.BREAK  # 事件结束，进入默认处理逻辑

    def get_help_text(self, **kwargs):
        return "赏析一句话。"


def get_quote():
    url = "https://v1.hitokoto.cn/"
    response = requests.get(url)
    js = response.json()
    words = js["hitokoto"]
    from_ = js["from"]
    who = js["from_who"]
    sentence = words
    if from_ is not None or who is not None:
        sentence += "——"
    if who is not None:
        sentence += who
    if from_ is not None:
        sentence += "《" + from_ + "》"
    return sentence
