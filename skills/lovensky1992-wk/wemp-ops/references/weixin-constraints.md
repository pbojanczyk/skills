# 微信公众号平台限制

## CSS 限制

微信编辑器**不支持**：
- 外部 CSS 文件（必须内联）
- `position: fixed/sticky`
- `@keyframes` 动画
- `calc()` 函数
- CSS 变量 `var()`
- `flexbox`（部分支持，不稳定）
- `grid` 布局

**支持的常用属性**：
- `color`, `background-color`, `background` 渐变
- `font-size`, `font-weight`, `line-height`, `letter-spacing`
- `margin`, `padding`, `border`, `border-radius`
- `text-align`, `text-indent`
- `display: inline/block/inline-block`
- `box-shadow`（部分客户端）
- `max-width`, `width`（百分比和 px）

## 图片限制

- 不支持本地图片路径，必须上传到微信素材库
- 封面图建议 900×500（2.35:1 也可）
- 单图 ≤ 2MB
- 支持格式：jpg/jpeg/png/gif
- 文章内图片会被微信压缩

## 内容限制

- 不支持 JavaScript
- 不支持 iframe
- 不支持外部链接（超链接只能链接到其他公众号文章或小程序）
- 所有链接在正文中用纯文本展示
- 不支持视频直接嵌入（需用微信视频功能）

## 排版建议

- 正文字号：15-17px
- 行高：1.75-2.0
- 段间距：通过 margin-bottom 控制
- 代码块用 `pre + code` + 背景色 + 内联样式
- 表格列数 ≤ 4（移动端友好）
- 全文内联样式写在每个标签的 `style` 属性中

## API 限制

- access_token 每日获取上限 2000 次（工具自动缓存）
- 草稿 API 无频率限制
- 群发消息：订阅号 1 次/天，服务号 4 次/月
- 素材上传：单文件 ≤ 2MB（图片）、≤ 10MB（视频）
