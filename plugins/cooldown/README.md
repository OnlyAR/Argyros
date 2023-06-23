## 插件描述

用于设置 cd，支持群组和私聊。

使用前将`config.json.template`复制为`config.json`，并自行配置。

目前插件对超过cd的处理行为有如下两种：

- `ignore`: 忽略消息
- `reset`: 重置cd

```json
{
  "action": "reset",
  "env": ["group", "single"],
  "admin_ignore": true,
  "cd": 30
}

```

在以上配置项中：

- `action`: 超过cd的处理行为
- `env`: 适用的环境
- `admin_ignore`: 是否忽略管理员
- `cd`: 默认cd时间