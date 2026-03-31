# meta-skill-weaver - 技能编织器

**版本**：v0.1.0  
**定位**：技能编排与任务执行引擎

---

## 📖 技能说明

meta-skill-weaver 是一个任务编排引擎，能够：
1. **分解复杂任务** - 将大任务分解为可执行的子任务
2. **分配合适技能** - 根据子任务类型分配合适技能
3. **追踪执行状态** - 实时追踪每个任务的进度
4. **支持中断恢复** - 任务中断后可从断点恢复
5. **收集优化数据** - 收集技能使用数据用于持续优化

---

## 🎯 使用场景

| 场景 | 示例任务 |
|------|----------|
| **多技能协作** | 「分析这个 GitHub 项目，生成报告，然后创建 PPT」 |
| **长程任务** | 「研究老钱家族决策模式，整合到技能中」 |
| **中断恢复** | 「继续昨天未完成的任务」 |
| **进度追踪** | 「当前任务执行到什么阶段了？」 |

---

## 🚀 使用方法

### 方式 1：直接调用

```
请编排执行以下任务：

[你的复杂任务]
```

### 方式 2：查看任务状态

```
查看当前所有任务状态
```

### 方式 3：恢复中断任务

```
恢复任务 [任务 ID]
```

---

## 📋 任务执行流程

```
┌─────────────────────────────────────────────────────────┐
│  阶段 1: 任务接收与分解                                   │
│  - 接收复杂任务                                          │
│  - AI 分析任务结构                                        │
│  - 分解为子任务                                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  阶段 2: 技能分配                                         │
│  - 分析每个子任务需要的技能                              │
│  - 检查技能可用性                                        │
│  - 分配执行顺序                                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  阶段 3: 执行与追踪                                       │
│  - 执行子任务 1                                          │
│  - 记录执行状态                                          │
│  - 传递数据到子任务 2                                     │
│  - ...                                                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  阶段 4: 数据收集                                         │
│  - 收集每个技能的执行数据                                │
│  - 记录执行时间、质量评分                                │
│  - 存储到优化知识库                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  阶段 5: 进度报告                                         │
│  - 生成任务进度报告                                      │
│  - 包含已完成/进行中/待执行                              │
│  - 可选：生成改进建议                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 与 first-principle-analyzer 的协作

```
用户任务：「优化 first-principle-analyzer 技能」

meta-skill-weaver 编排流程：
1. 分解任务：
   - 子任务 1：分析当前版本的局限
   - 子任务 2：搜集改进灵感
   - 子任务 3：设计改进方案
   - 子任务 4：实施改进
   - 子任务 5：验证效果

2. 分配技能：
   - 子任务 1 → first-principle-analyzer (自省分析)
   - 子任务 2 → 每日搜集任务 (从知识库获取)
   - 子任务 3 → first-principle-analyzer (重构方案)
   - 子任务 4 → skill-creator (实施改进)
   - 子任务 5 → skill-curator (评估效果)

3. 追踪状态：
   - 实时记录每个子任务的进度
   - 支持中断恢复

4. 收集数据：
   - 记录每个技能的执行时间
   - 记录用户满意度评分
   - 用于未来优化
```

---

## 🔧 任务状态定义

| 状态 | 说明 |
|------|------|
| **pending** | 等待执行 |
| **running** | 正在执行 |
| **blocked** | 被阻塞（等待依赖） |
| **completed** | 已完成 |
| **failed** | 执行失败 |
| **paused** | 已暂停（可恢复） |

---

## 📈 优化数据收集

收集的數據类型：

| 数据类型 | 用途 |
|----------|------|
| 执行时间 | 识别性能瓶颈 |
| 技能调用次数 | 识别常用/少用技能 |
| 用户满意度 | 评估技能质量 |
| 错误类型 | 识别常见问题 |
| 中断频率 | 识别任务复杂度问题 |

---

## ⚠️ 使用注意

### 何时使用
- ✅ 复杂任务需要多个技能协作
- ✅ 长程任务需要状态追踪
- ✅ 需要中断恢复能力
- ✅ 需要收集优化数据

### 何时不使用
- ❌ 简单单步骤任务（直接用技能）
- ❌ 紧急任务（编排有开销）

---

## 📚 版本演进

完整版本历史见：[VERSION_HISTORY.md](./VERSION_HISTORY.md)

### 当前版本：v0.1.0
- 任务分解与分配
- 状态追踪
- 中断恢复
- 数据收集

### 下一版本：v0.2.0 (规划中)
- 可视化工作流编排
- 技能接口标准化
- 自动优化建议

---

**创建时间**：2026-03-27  
**创建者**：王的奴隶 · 严谨专业版  
**灵感来源**：DeerFlow Super Agent、Linux Kernel 模块调用  
**版本**：v0.1.0

---

## 🆕 v0.2.0 新增功能（学习 DeerFlow）

### Middleware 链

受 DeerFlow 的 9 个 Middleware 启发，我们实现了 Middleware 链：

```javascript
const { MiddlewareChain, loggingMiddleware, validationMiddleware, timeoutMiddleware } = require('./src/middleware-chain');

const chain = new MiddlewareChain();

chain
  .use(loggingMiddleware(), 'Logging')
  .use(validationMiddleware(), 'Validation')
  .use(timeoutMiddleware(300000), 'Timeout (5min)');

const result = await chain.execute(taskState);
```

**内置 Middleware**：
- loggingMiddleware - 记录执行日志
- validationMiddleware - 验证任务输入
- timeoutMiddleware - 设置超时
- errorHandlingMiddleware - 错误处理和重试
- cacheMiddleware - 缓存结果
- contextInjectionMiddleware - 注入上下文
- memoryInjectionMiddleware - 注入记忆

### 虚拟路径系统

受 DeerFlow 的虚拟路径映射启发：

```javascript
const { VirtualPathSystem } = require('./src/virtual-path-system');

const vps = new VirtualPathSystem('/base/dir');

// 挂载虚拟路径
vps.mount('/mnt/skills', '/actual/skills/path');

// 创建线程隔离目录
const threadPaths = await vps.createThreadDir('thread-123');
// 返回：{ workspace, uploads, outputs }

// 解析路径
const physicalPath = vps.resolve('/mnt/skills/my-skill');
```

### 并发执行

受 DeerFlow 的 asyncio.gather 启发：

```javascript
const { ParallelExecutor } = require('./src/parallel-execution');

const executor = new ParallelExecutor(
  3,  // 最大并发数
  15 * 60 * 1000  // 超时 15 分钟
);

const results = await executor.executeParallel(tasks, executeFn);
```

**特性**：
- 限制并发数（默认 3 个）
- 超时控制（默认 15 分钟）
- 错误处理（失败不影响其他任务）
- 结果收集（成功/失败都记录）

---

**更新时间**：2026-03-27 20:53  
**版本**：v0.2.0（DeerFlow 学习版）

---

## 💰 购买与授权

**本技能版本**：v0.2.0（增强版）

**授权类型**：
- **个人版**：$99.9（永久使用，个人非商业用途）
- **商业版**：$299.9（永久使用，商业用途）
- **企业版**：$999.9（永久使用 + 定制支持）

**购买后获得**：
- ✅ 技能完整源码（4 个 JS 文件）
- ✅ Middleware 链（7 个内置）
- ✅ 虚拟路径系统
- ✅ 并发执行模块
- ✅ 使用文档
- ✅ 1 年免费更新
- ✅ 邮件支持

**购买方式**：
1. 访问 ClawHub 技能页面
2. 选择授权类型
3. 支付（支付宝/微信/PayPal）
4. 自动获得授权码

**联系方式**：
- 📧 邮箱：support@cloud-shrimp.com
- 💬 微信：CloudShrimpSupport（备注：技能名称）
- 🐦 Twitter：@CloudShrimpAI
- 💻 GitHub：github.com/cloud-shrimp

**企业定制**：
- 技能定制开发：¥20,000 起
- 技术咨询：¥1,500/小时
- 请联系：business@cloud-shrimp.com

---

**技能版本**：v0.2.0  
**创建时间**：2026-03-27  
**维护者**：王的奴隶 · 严谨专业版  
**授权**：商业许可（购买后）
