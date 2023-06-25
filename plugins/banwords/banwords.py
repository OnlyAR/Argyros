# encoding:utf-8

import json
import os

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *


@plugins.register(
    name="Banwords",
    desire_priority=100,
    hidden=True,
    desc="判断消息中是否有敏感词、决定是否回复。",
    version="1.0",
    author="lanvent",
)
class Banwords(Plugin):

    def __init__(self):
        super().__init__()
        try:
            curdir = os.path.dirname(__file__)
            config_path = os.path.join(curdir, "config.json")
            conf = None
            if not os.path.exists(config_path):
                conf = {"action": "ignore"}
                with open(config_path, "w", encoding="utf8") as f:
                    json.dump(conf, f, indent=4)
            else:
                with open(config_path, "r", encoding="utf8") as f:
                    conf = json.load(f)
            self.action = conf["action"]
            # 修改设置，违禁词从config.json中读取
            # banwords_path = os.path.join(curdir, "banwords.txt")
            with open(config_path, "r", encoding="utf-8") as f:
                # words = []
                # for line in f:
                #     word = line.strip()
                #     if word:
                #         words.append(word)
                self.words = conf["word_group"]
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            if conf.get("reply_filter", True):
                self.handlers[Event.ON_DECORATE_REPLY] = self.on_decorate_reply
                self.reply_action = conf.get("reply_action", "ignore")
            logger.info("[Banwords] inited")
        except Exception as e:
            logger.warn(
                "[Banwords] init failed, ignore or see https://github.com/zhayujie/chatgpt-on-wechat/tree/master/plugins/banwords .")
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
            ContextType.IMAGE_CREATE,
        ]:
            return

        if not e_context["context"].get("isgroup", False):
            return

        content = e_context["context"].content
        logger.debug("[Banwords] on_handle_context. content: %s" % content)
        if self.action == "ignore":
            msg = self._get_forbid_result(content)
            if msg is not None:
                logger.info("[Banwords] %s in message" % msg)
                e_context.action = EventAction.BREAK_PASS
                return
        elif self.action == "replace":
            msg = self._get_forbid_result(content)
            if msg is not None:
                reply = Reply(ReplyType.TEXT, msg)
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
                return

    def on_decorate_reply(self, e_context: EventContext):
        if e_context["reply"].type not in [ReplyType.TEXT]:
            return

        if not e_context["context"].get("isgroup", False):
            return

        reply = e_context["reply"]
        content = reply.content
        if self.reply_action == "ignore":
            msg = self._get_forbid_result(content)
            if msg is not None:
                logger.info("[Banwords] %s in message" % msg)
                e_context["reply"] = None
                e_context.action = EventAction.BREAK_PASS
                return
        elif self.reply_action == "replace":
            msg = self._get_forbid_result(content)
            if msg is not None:
                reply = Reply(ReplyType.TEXT, content.split()[0] + " " + msg)
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
                return

    def get_help_text(self, **kwargs):
        return "过滤消息中的敏感词。"

    def _get_forbid_result(self, content: str):
        for key, item in self.words.items():
            for word in item['words']:
                if word in content:
                    return item['reply']
        return None
