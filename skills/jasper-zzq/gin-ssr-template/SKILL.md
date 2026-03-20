---
name: gin-ssr-template
description: 根据 Figma 设计稿生成 Gin SSR 服务端渲染模板（HTML + CSS）。当用户发送 "gin前端模板" 或提供 Figma 页面截图时激活，生成符合 项目规范的模板文件。
---

# Gin SSR 前端模板生成（Open Claw）

> ⚠️ 本 skill 专供 Open Claw 使用，不适用于 Cursor。

根据 Figma 截图生成符合 项目架构的 HTML + CSS 文件。

## 激活方式

当用户发送 "gin前端模板" 或提供 Figma 页面截图时，自动执行此 skill。

## 截图处理规则

> 优先处理 PC 设计稿，其次处理 H5 设计稿。

1. **单张截图**：直接根据截图生成模板
2. **两张截图（PC + H5）**：
   - 以 PC 截图为主模板，生成基础 HTML + CSS
   - 以 H5 截图作为响应式适配参考，补充 `@media (max-width: 824px)` 样式
3. **只有 H5 截图**：正常生成，在 CSS 中使用 `@media (min-width: 825px)` 定义 PC 样式

## 输出规范

- **文件名**：HTML 文件名按 Figma 页面命名（如 `xxx.html`），CSS 文件名对应（如 `xxx.css`）
- **文件路径**：
  - HTML: `app/templates/page/{页面名}.html`
  - CSS: `app/static/css/{页面名}.css`
- **输出语言**：代码注释使用中文

## HTML 模板结构

### 1. SEO 元信息（`<head>` 部分）

```html
{{define "页面名"}}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge, chrome=1" />
    <meta name="renderer" content="webkit" />
    <meta name="HandheldFriendly" content="true" />
    <meta name="referrer" content="same-origin" />

    <title>{{.data.Config.WebTitle}}</title>
    <meta name="description" content="{{.data.Config.WebDescription}}" />
    <meta name="keywords" content="{{INJoinKeyworld .data.Config.WebKeyworld}}" />
    <link rel="canonical" href="{{.data.Config.ForeverUrlAddr}}{{.data.Path}}" />
    <meta name="robots" content="{{InGetRobotsTag .data.PageNum}}" />
    <meta name="rating" content="adult" />
    <meta name="template" content="Mirages" />

    <meta property="og:title" content="{{.data.Config.WebTitle}}" />
    <meta property="og:site_name" content="{{.data.Config.WebSiteName}}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{{.data.Config.ForeverUrlAddr}}{{.data.Path}}" />
    <meta property="og:image" content="{{.data.Config.ForeverUrlAddr}}/favicon.ico" />
    <meta property="og:description" content="{{.data.Config.WebDescription}}" />

    <meta name="theme-color" content="#ffffff" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="#ffffff" />
    <link rel="shortcut icon" href="{{.data.Config.ForeverUrlAddr}}/favicon.ico" />
    <link rel="icon" type="image/x-icon" href="{{.data.Config.ForeverUrlAddr}}/favicon.ico" />

    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@graph": [
          {
            "@type": "Organization",
            "@id": "{{.data.Config.ForeverUrlAddr}}/#org",
            "name": "{{.data.Config.WebSiteName}}",
            "url": "{{.data.Config.ForeverUrlAddr}}",
            "logo": {
              "@type": "ImageObject",
              "url": "{{.data.Config.ForeverUrlAddr}}/static/images/logo.png"
            }
          },
          {
            "@type": "WebSite",
            "@id": "{{.data.Config.ForeverUrlAddr}}/#website",
            "url": "{{.data.Config.ForeverUrlAddr}}",
            "name": "{{.data.Config.WebSiteName}}",
            "inLanguage": "zh-CN",
            "publisher": { "@id": "{{.data.Config.ForeverUrlAddr}}/#org" },
            "potentialAction": {
              "@type": "SearchAction",
              "target": "{{.data.Config.ForeverUrlAddr}}/{search_term_string}",
              "query-input": "required name=search_term_string"
            }
          }
        ]
      }
    </script>

    <script src="/static/js/imgDecypt.js"></script>
    <script src="/static/js/index.js"></script>
    <script src="/static/js/bootstrap.bundle.min.js"></script>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css" />
    <link rel="stylesheet" href="/static/css/style.css" />
    <link rel="stylesheet" href="/static/css/{页面名}.css" />
  </head>
</html>
```

### 2. 页面内容（`<body>` 部分）

```html
<body>
  <header>{{template "pcNav" .data}}</header>

  <main>
    <!-- 页面具体内容 -->
  </main>

  <footer>{{template "bottomNav" .}}</footer>
</body>
```

### 3. 底部脚本（`</html>` 前）

```html
  <script src="/static/js/gtm.js"></script>
</html>
{{end}}
```

### JSON-LD 结构说明

JSON-LD 根据页面类型在 `@graph` 数组中添加不同节点：

| 页面类型    | `@type`          | 额外字段                                       |
| ----------- | ---------------- | ---------------------------------------------- |
| 首页/列表页 | `CollectionPage` | `description`, `isPartOf`, `about`             |
| 详情页      | `Article`        | `headline`, `image`, `datePublished`, `author` |

**列表页示例（追加到 @graph）**：

```json
{
  "@type": "CollectionPage",
  "@id": "{{.data.Config.ForeverUrlAddr}}/#webpage",
  "url": "{{.data.Config.ForeverUrlAddr}}{{.data.Path}}",
  "name": "{{.data.Config.WebTitle}}",
  "description": "{{.data.Config.WebDescription}}",
  "inLanguage": "zh-CN",
  "isPartOf": { "@id": "{{.data.Config.ForeverUrlAddr}}/#website" },
  "about": { "@id": "{{.data.Config.ForeverUrlAddr}}/#org" }
}
```

**详情页示例（追加到 @graph）**：

```json
{
  "@type": "Article",
  "@id": "{{.data.Config.ForeverUrlAddr}}{{.data.Path}}/#article",
  "headline": "{{.data.Config.WebTitle}}",
  "description": "{{.data.Config.WebDescription}}",
  "image": "{{.data.Config.ForeverUrlAddr}}/favicon.ico",
  "datePublished": "{{InFormatDateStringDash .data.PublishTime}}",
  "author": { "@id": "{{.data.Config.ForeverUrlAddr}}/#org" },
  "publisher": { "@id": "{{.data.Config.ForeverUrlAddr}}/#org" },
  "inLanguage": "zh-CN",
  "isPartOf": { "@id": "{{.data.Config.ForeverUrlAddr}}/#website" }
}
```

## CSS 规范

### 文件命名

- 文件名与 HTML 页面名一致
- 放在 `app/static/css/` 目录下

### 布局规范

> CSS 的主要目标是精确还原截图中的视觉样式，无需限制宽度或内边距。

| 规范     | 值                     |
| -------- | ---------------------- |
| 容器宽度 | 由截图决定，不强制限制 |
| 内边距   | 由截图决定，不强制添加 |
| PC 端    | `min-width: 824px`     |
| H5 端    | `max-width: 824px`     |

### 样式还原原则

- **尺寸/间距**：严格按截图中的像素值还原，包括 `width`、`height`、`margin`、`padding`
- **字体**：还原 `font-size`、`font-weight`、`color`、`line-height`
- **颜色**：精确还原所有 `color`、`background-color`、`border-color` 等颜色值
- **布局**：优先使用 Flexbox 或 Grid 实现与截图一致的布局效果
- **图片/图标**：保持截图中的宽高比和比例
- **不自动添加**：`max-width`、`margin: auto` 等约束性样式，除非截图中有明确体现

### 双端样式差异

```css
/* PC 端样式（> 824px） */
.element {
  /* PC 端样式 */
}

/* H5 端样式（≤ 824px） */
@media screen and (max-width: 824px) {
  .element {
    /* H5 端样式 */
  }
}
```

## 可用模板函数

| 函数                     | 用途                                  | 示例                                        |
| ------------------------ | ------------------------------------- | ------------------------------------------- |
| `InToJSON .data`         | 调试输出 JSON                         | `{{InToJSON .data}}`                        |
| `InDict k1 v1 k2 v2`     | 构建 map 传递给模板                   | `{{InDict "Name" "标题" "Media" .list}}`    |
| `InRichText`             | 富文本转 HTML                         | `{{InRichText .content}}`                   |
| `InFormatDate`           | 格式化为 `2006.01.02 15:04`           | `{{InFormatDate .time}}`                    |
| `InFormatYm`             | 格式化为 `2006年01月`                 | `{{InFormatYm .time}}`                      |
| `InFormatTime`           | 自定义格式时间                        | `{{InFormatTime .time "2006-01-02"}}`       |
| `InFormatDuration`       | 格式化视频时长 `00:00`                | `{{InFormatDuration .duration}}`            |
| `InFormatDateString`     | `2006年01月02日`                      | `{{InFormatDateString .date}}`              |
| `InFormatDateStringSep`  | `2006/01/02`                          | `{{InFormatDateStringSep .date}}`           |
| `InFormatDateStringDash` | `YYYY-MM-DD`                          | `{{InFormatDateStringDash .date}}`          |
| `ImgDecrypt`             | 图片 XOR 解密（**网络图片必须使用**） | `{{ImgDecrypt .imgUrl}}`                    |
| `InPage`                 | 计算分页总数                          | `{{InPage .data.TotalSize .data.PageSize}}` |
| `ChangeNum`              | 数字换算（万/亿）                     | `{{ChangeNum .viewCount "万"}}`             |
| `INJoinKeyworld`         | 合并关键词                            | `{{INJoinKeyworld .keywords}}`              |
| `InPageTitleSuffix`      | 页面标题后缀                          | `{{InPageTitleSuffix .pageNum}}`            |
| `InGetRobotsTag`         | robots meta 标签                      | `{{InGetRobotsTag .pageNum}}`               |
| `InformatCount`          | 数字展示（1000→1k, 10000→1w）         | `{{InformatCount .views}}`                  |
| `Seq n`                  | 生成 0~n-1 序列                       | `{{range Seq 10}}`                          |
| `InSub/InAdd`            | 数值加减                              | `{{InSub .a .b}}`                           |
| `InMod i j`              | 取模运算                              | `{{InMod .index 2}}`                        |
| `InNumberToChinese`      | 数字转中文（1→一）                    | `{{InNumberToChinese .index}}`              |
| `InNumberToChineseFull`  | 数字转完整中文                        | `{{InNumberToChineseFull .num}}`            |
| `template "name" .data`  | 嵌套模板                              | `{{template "pcNav" .data}}`                |

## 常见内容模块模板

### 网络图片（必须使用）

```html
<!-- 网络图片必须使用 ImgDecrypt 解密，并添加 lazy 属性 -->
<img loading="" lazy src="{{ImgDecrypt .imgUrl}}" alt="{{.alt}}" />
```

### 本地/内链图片

```html
<!-- 非加密图片直接使用 -->
<img src="{{.imgUrl}}" alt="{{.alt}}" />
```

### 列表项（图片+标题+标签）

```html
{{range .data.List}}
<div class="section-content__item">
  <div class="item-cover">
    <a href="{{.Href}}">
      <img loading="" lazy src="{{ImgDecrypt .Cover}}" alt="{{.Title}}" />
    </a>
  </div>
  <div class="item-texts">
    <h3 class="text-ellipsis-1">{{.Title}}</h3>
    {{if .Tags}}
    <div class="text-social">
      {{range .Tags}}
      <span>{{.}}</span>
      {{end}}
    </div>
    {{end}}
  </div>
</div>
{{end}}
```

### 分页组件

```html
<!-- 直接调用已有的分页模板 -->
{{template "pagination" .data}}
```

## ⚠️ 重要：数据字段取值规则

> `.data` 是后端返回的结构体，**必须严格按照后端提供的结构体字段取值**。

### 正确流程

1. **用户提供 Figma 截图 + 后端结构体（如 `app/api/proto/*.go`）时**
   - 页面所有字段取值必须参考后端结构体定义
   - 不能凭猜测使用字段名
   - 如字段命名不明确，在生成前询问用户

2. **只有 Figma 截图，没有结构体时**
   - 使用通用字段名（如 `.Title`、`.Cover`、`.Href`）
   - 在注释中标注 `[字段名待确认]`
   - 提醒用户提供后端结构体

### 取值示例

```html
<!-- 根据结构体 ComicsInfoData 取值 -->
<img loading="" lazy src="{{ImgDecrypt .CoverImg}}" alt="{{.Title}}" />
<span>{{.Author}}</span>
<span>{{.ChapterCount}}话</span>

<!-- 根据结构体 ComicsCategoryHtmlData 取值 -->
{{range .ComicsInfos}}
<div class="item">
  <a href="/comics/{{.Jmid}}/">
    <img loading="" lazy src="{{ImgDecrypt .CoverImg}}" alt="{{.Title}}" />
  </a>
</div>
{{end}}
```

## 生成流程

1. 分析用户提供的 Figma 截图或页面需求
2. **如果有后端结构体文件**：读取并严格按字段名生成模板
3. 确定页面名称（用于文件名和 `{{define}}`）
4. 提取 SEO 信息（标题、描述、关键词）
5. 识别页面结构（header、main、footer、section 数量）
6. 确定 CSS 类名规范（参考现有 CSS）
7. 根据页面类型选择 JSON-LD 结构（CollectionPage / Article）
8. 生成 HTML 文件（SEO + 内容 + 脚本）
9. 生成 CSS 文件（PC 样式 + H5 适配）
10. 确认文件路径

## 注意事项

- 所有 CSS 类名需参考 `homeSection.css` 的命名规范
- 图片解密使用 `ImgDecrypt` 函数
- JSON-LD 结构化数据根据页面类型调整 `@type`
- 所有 `<a>` 链接需使用项目内路由格式
