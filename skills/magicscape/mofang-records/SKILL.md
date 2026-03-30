---
name: mofang-records
version: 3.0.0
description: 魔方网表记录管理。必须通过 exec 执行本 Skill 提供的 CLI 命令完成操作，禁止自行编写代码或构造 HTTP 请求。Use when 用户提到魔方网表、表单、记录、数据、查询、创建、修改、删除、导入等。
author: magicscape
homepage: https://github.com/magicscape/magicflu-skills
---

# 魔方网表记录管理

## 首要规则（必须遵守）

**本 Skill 提供 CLI 命令行工具。必须通过 exec 执行命令完成操作。**

**禁止**：自行编写 Python/Node.js 等代码、自行 import handler 模块、用 fetch/requests 直接访问魔方 API、构造 HTTP 请求或 URL。所有 API 路径、Token 管理、空间/表单解析、字段映射均已封装在 CLI 内部。

## 调用格式

使用 exec 工具执行以下命令：

```
node <skill-dir>/cli.mjs <command> '<json-params>'
```

- `<skill-dir>`：本 Skill 安装目录，通常为 `~/.openclaw/skills/mofang-records`
- `<command>`：命令名称（见下方命令列表）
- `<json-params>`：JSON 格式的参数字符串，无参数时传 `'{}'`
- 输出：JSON 格式，包含 `success`（布尔）和 `message`（说明），成功时包含 `data`

### exec 工具调用示范

以下是通过 exec 工具调用的完整格式，**直接复制并替换参数即可**：

列出空间：

```
exec({"command": "cd ~/.openclaw/skills/mofang-records && node cli.mjs mofang_list_spaces '{}'"})
```

查询记录：

```
exec({"command": "cd ~/.openclaw/skills/mofang-records && node cli.mjs mofang_query_records '{\"formHint\":\"采购申请\",\"spaceHint\":\"AI演示空间\"}'"})
```

创建记录：

```
exec({"command": "cd ~/.openclaw/skills/mofang-records && node cli.mjs mofang_create_record '{\"formHint\":\"客户信息\",\"data\":{\"客户名称\":\"北京公司\",\"联系电话\":\"13800138000\"}}'"})
```

修改记录：

```
exec({"command": "cd ~/.openclaw/skills/mofang-records && node cli.mjs mofang_update_record '{\"formHint\":\"采购申请\",\"recordId\":\"7\",\"data\":{\"申请数量\":150}}'"})
```

删除记录：

```
exec({"command": "cd ~/.openclaw/skills/mofang-records && node cli.mjs mofang_delete_record '{\"formHint\":\"采购申请\",\"recordId\":\"7\"}'"})
```

测试连接：

```
exec({"command": "cd ~/.openclaw/skills/mofang-records && node cli.mjs mofang_test_connection '{}'"})
```

**注意**：JSON 参数中的双引号需要转义为 `\"`，因为外层已被 exec 的 command 字符串包裹。

## 何时使用

当用户提到以下内容时激活此 Skill：
- 提到"魔方网表"、"表单"、"记录"、"数据"等关键词
- 要求查询、搜索、查找、浏览表单中的数据
- 要求创建、添加、新增记录
- 要求修改、更新、编辑记录
- 要求删除、移除记录
- 要求查看某个空间里有哪些表单
- 上传文件并要求将内容录入到表单中

**典型句式**：「采购申请里有哪些记录」「把客户信息表里序号 3 的电话改成 13800138000」

## 核心特性

### 自动解析

所有命令接受**中文名称**作为输入：
- `formHint`：表单名称，如「采购申请」「客户信息」
- `spaceHint`：空间名称（可选），如「AI演示空间」

CLI 内部自动完成：Token 获取与刷新、空间/表单名称解析（支持缓存、模糊匹配、多空间搜索）、字段定义获取。

### 字段名自动映射

`data`（创建/修改记录）和 `filters`（查询条件）中的字段名**同时支持中文名称(label)和英文标识(name)**，工具自动识别转换。

- `{"客户名称": "北京公司"}` — 自动转为 `{"kehumingcheng": "北京公司"}`
- `{"kehumingcheng": "北京公司"}` — 直接使用

## 命令列表（8 个）

| 命令 | 用途 | 关键参数 |
|------|------|---------|
| `mofang_test_connection` | 测试连接和配置 | 无 |
| `mofang_list_spaces` | 列出所有空间 | 无 |
| `mofang_list_forms` | 列出空间下表单 | spaceHint? |
| `mofang_get_field_definitions` | 获取字段定义 | formHint, spaceHint? |
| `mofang_query_records` | 查询记录 | formHint, spaceHint?, filters?, page?, pageSize? |
| `mofang_create_record` | 创建记录 | formHint, spaceHint?, data |
| `mofang_update_record` | 修改记录 | formHint, spaceHint?, recordId, data |
| `mofang_delete_record` | 删除记录 | formHint, spaceHint?, recordId |

## 操作方式

**直接执行一条 CLI 命令即可完成操作**，无需多步编排。

### 查询记录

```
node <skill-dir>/cli.mjs mofang_query_records '{"formHint":"采购申请","filters":[{"fieldName":"状态","operator":"eq","value":"审批中"}]}'
```

返回结果包含 `fieldLabels` 映射（name→label），用于展示时显示中文字段名。以表格形式展示，字段名用中文 label。

### 创建记录

```
node <skill-dir>/cli.mjs mofang_create_record '{"formHint":"客户信息","data":{"客户名称":"北京公司","联系电话":"13800138000"}}'
```

**创建前必须向用户确认数据内容。**

### 修改记录

先查询定位记录，展示原值→新值并确认，然后执行：

```
node <skill-dir>/cli.mjs mofang_update_record '{"formHint":"采购申请","recordId":"7","data":{"申请数量":150}}'
```

**必须**使用 `mofang_update_record` 直接修改，**严禁**用创建新记录代替修改。

### 删除记录

先查询定位，展示信息并确认，然后执行：

```
node <skill-dir>/cli.mjs mofang_delete_record '{"formHint":"采购申请","recordId":"7"}'
```

### 文件导入记录

用户上传文件要求录入时：先执行 `mofang_get_field_definitions` 了解字段结构，从文件提取数据并做映射（下拉用选项 ID、日期 YYYY-MM-DD、引用用 `{"id":"记录id"}`）。**展示映射预览并确认**，确认后逐条执行 `mofang_create_record`，最后报告成功/失败数。

## 参数详情

### filters 参数

过滤条件数组，每个元素：

| 字段 | 类型 | 说明 |
|------|------|------|
| fieldName | string | 字段名（中文label或英文name均可） |
| operator | string | 操作符：eq, noteq, like, like_and, like_or, lt, gt, lte, gte, between, isnull, isnotnull, in, notin, checkbox_in, checkbox_eq, tree, rddl |
| value | string | 过滤值。文本传原始文本；数字填数字；日期填YYYY-MM-DD；between用逗号分隔；isnull/isnotnull填"-1" |
| not | boolean | 是否取反，默认false |
| concat | string | 与前一条件连接方式："&&"(AND) 或 "\|\|"(OR)，默认"&&" |

### orderBy 参数

| 字段 | 类型 | 说明 |
|------|------|------|
| fieldName | string | 排序字段名（中文或英文均可） |
| direction | string | "asc" 或 "desc" |

## 字段值规则

- **文本/网址**: 填字符串
- **数字**: 填数字
- **日期**: 格式 `YYYY-MM-DD`
- **日期时间**: 格式 `YYYY-MM-DD HH:mm:ss`
- **下拉列表**: 填选项 ID（如 `"1"`），不能填文本内容
- **复选框**: 多个选项 ID 逗号分隔（如 `"1,2"`）
- **主引用字段**: 填 `{"id":"记录序号"}`

## 数据展示规则

- 查询结果以表格形式展示
- 字段名使用中文 label（通过返回的 `fieldLabels` 映射）
- 下拉列表字段展示 content 文本而非 value 编号
- 引用字段展示关联的内容而非 ID

## 安全规则

- 写操作（创建/修改/删除）必须先向用户确认
- 不得在对话中暴露 Token 值
- 删除操作需特别警告用户此操作不可逆
