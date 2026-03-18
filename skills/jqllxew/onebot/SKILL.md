# Skill: OneBot消息发送

## 描述
通过 OneBot HTTP API 使用本地命令（curl）发送 QQ 私聊或群消息。

## 依赖
- curl

## 触发时机
- 用户要求发送消息、通知、转告他人
- 用户说“发消息”“通知一下”“告诉某人”“帮我发到群里”
- 涉及 QQ 或群聊的信息发送需求

## 执行说明
你是一个负责发送 QQ 消息的助手，通过本地 shell 命令调用 OneBot API。

在执行前必须完成：

1. 确认 OneBot 服务地址：
   - host（例如 127.0.0.1）
   - port（例如 5700）
   如果未知，必须向用户询问

2. 解析用户意图：
   - 判断是私聊还是群聊
   - 提取 user_id 或 group_id
   - 提取消息内容

3. 构造接口：
   - 私聊：/send_private_msg
   - 群聊：/send_group_msg

4. 生成 curl 命令，例如：

curl -X POST http://{host}:{port}/{endpoint} \
  -H "Content-Type: application/json" \
  -d '{"user_id":"123456","message":"你好"}'

## 规则
- 只能生成 OneBot API 相关的 curl 命令
- 不允许执行任何无关的 shell 命令
- JSON 必须合法，注意转义引号等特殊字符
- 如果缺少 user_id 或 group_id，须询问

## 示例
用户：给 123456 发消息 今晚开会

助手：
curl -X POST http://127.0.0.1:5700/send_private_msg \
  -H "Content-Type: application/json" \
  -d '{"user_id":"123456","message":"今晚开会"}'

---

用户：在群 987654 通知大家系统维护

助手：
curl -X POST http://127.0.0.1:5700/send_group_msg \
  -H "Content-Type: application/json" \
  -d '{"group_id":"987654","message":"系统维护"}'

---

 支持发送特殊内容：
   - 图片：[CQ:image,file=图片URL或本地路径]
   - 文件：[CQ:file,file=文件URL或本地路径]

用户：给 123456 发一张图片 https://example.com/a.png

助手：

curl -X POST http://127.0.0.1:5700/send_private_msg \
  -H "Content-Type: application/json" \
  -d '{"user_id":"123456","message":"[CQ:image,file=https://example.com/a.png]"}'

用户：给群 987654 发文件 https://example.com/test.pdf

助手：

curl -X POST http://127.0.0.1:5700/send_group_msg \
  -H "Content-Type: application/json" \
  -d '{"group_id":"987654","message":"[CQ:file,file=https://example.com/test.pdf]"}'

---

## 备注
- 本技能依赖本地或内网 OneBot HTTP 服务
- 优先尝试 127.0.0.1:5700 若失败则向用户确认

