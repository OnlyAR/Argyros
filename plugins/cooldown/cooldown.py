# encoding:utf-8

import json
import os
import time

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *


@plugins.register(
    name="Cooldown",
    desire_priority=200,
    hidden=False,
    desc="设置cd，防止刷屏",
    version="1.0",
    author="Only(AR)",
)
class Cooldown(Plugin):
    def __init__(self):
        super().__init__()
        try:
            curdir = os.path.dirname(__file__)
            config_path = os.path.join(curdir, "config.json")
            conf = None
            if not os.path.exists(config_path):
                conf = {
                    "action": "reset",
                    "env": ["group", "single"],
                    "admin_ignore": True,
                    "cd": 30
                }
                with open(config_path, "w", encoding="utf8") as f:
                    json.dump(conf, f, indent=4)
            else:
                with open(config_path, "r", encoding="utf8") as f:
                    conf = json.load(f)
            self.action = conf["action"]
            self.env = conf["env"]
            self.admin_ignore = conf["admin_ignore"]
            self.cd = conf["cd"]
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.last_time = {}
            logger.info("[cooldown] inited")
        except Exception as e:
            logger.warn("[cooldown] init failed")
            logger.warn(e)
            raise e

    def on_handle_context(self, e_context: EventContext):
        # 拦截所有非文本消息
        if e_context["context"].type != ContextType.TEXT:
            e_context["reply"] = None
            e_context.action = EventAction.BREAK_PASS
            return
        in_group = not e_context["context"].get("isgroup", False)
        in_single = not in_group
        admin_list = PluginManager().instances["GODCMD"].admin_users
        is_admin = e_context["context"]["receiver"] in admin_list

        if is_admin:
            if e_context["context"].type == ContextType.TEXT:
                content = e_context["context"].content.strip()
                if content.startswith("$"):
                    cmds = content[1:].split()
                    if len(cmds) == 2 and cmds[0] == "setcd":
                        try:
                            seconds = int(cmds[1])
                            self.cd = seconds
                            reply = Reply(ReplyType.INFO, "冷却时间已设置为{}秒喵~".format(seconds))
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS
                        except Exception:
                            reply = Reply(ReplyType.INFO, "设置冷却时间失败喵~")
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS

        current_time = time.time()
        delta = current_time - self.last_time.get(e_context["context"]["receiver"], 0)

        if self.action == "reset":
            self.last_time[e_context["context"]["receiver"]] = current_time

        if delta <= self.cd:
            if not (self.admin_ignore and is_admin):
                if "group" in self.env and in_group or "single" in self.env and in_single:
                    reply = Reply(ReplyType.TEXT, "冷却中，还剩{}秒喵~".format(int(self.cd - delta)))
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
                    return

        if self.action == "ignore":
            self.last_time[e_context["context"]["receiver"]] = current_time

        if e_context["context"].type == ContextType.TEXT:
            content = e_context["context"].content.strip()
            if content.startswith("$"):
                cmds = content[1:].split()
                if len(cmds) == 1 and cmds[0] == "getcd":
                    reply = Reply(ReplyType.INFO, "当前冷却时间为{}秒喵~".format(self.cd))
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
                    return

    def get_help_text(self, verbose=False, **kwargs):
        help_text = "设置cd，防止刷屏"
        if not verbose:
            return help_text
        help_text += "\n$getcd 获取当前冷却时间"
        return help_text
