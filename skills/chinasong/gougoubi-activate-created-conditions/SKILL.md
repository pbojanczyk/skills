---
name: gougoubi-activate-created-conditions
description: Activate all CREATED conditions under a Gougoubi proposal by voting from a BNB address, with deterministic checks for committee membership and auto-staking minimum requirement before voting. Use when users ask to vote/activate proposal conditions by proposal id.
metadata: {"clawdbot":{"emoji":"🗳️","os":["darwin","linux","win32"]}}
---

# Gougoubi 激活提案条件（批量投票）技能

当用户要求「给定提案 id，使用一个 BNB 地址去激活该提案下所有已创建条件」时，使用本技能。

## 何时使用

- 用户说：按提案 id 投票激活条件、激活某提案下所有已创建条件、用某个地址给提案条件投票等。
- 输入：`proposalId`（提案 id）、`bnbAddress`（BSC 上的钱包地址）；可选 `minBnbForGas`、`approve`。

## 目标

在一个确定性流程里完成以下动作：

1. 校验输入（`proposalId`、`bnbAddress`）
2. 校验该地址是否为提案委员会成员
3. 若不是成员，则按最小要求自动质押加入委员会
4. 找出该提案下所有 `CREATED` 状态条件
5. 对这些条件逐个执行 `voteOnConditionActivation(condition, true)`
6. 返回结构化结果与失败提示

## 输入契约（必填）

```json
{
  "proposalId": "number|string, required",
  "bnbAddress": "0x... EVM address on BSC, required"
}
```

可选参数：

```json
{
  "approve": "boolean, default true",
  "minBnbForGas": "string in ether, default 0.001"
}
```

**调用示例**（用户或 Agent 提供）：

- 「用 0x1234... 这个地址把提案 5 下所有已创建条件投票激活」
- 结构化输入：`{ "proposalId": 5, "bnbAddress": "0x1234..." }`

## 关键约束

- 链：BSC Mainnet（chainId 56）
- 必须使用该 `bnbAddress` 对应钱包签名，不能代签
- 提案委员会成员校验：`Factory.isProposalCommitteeMember(proposal, bnbAddress)`
- 最小入会质押：`Factory.getProposalCommitteeMinStakeToJoin(proposal)`
- 仅投票 `CREATED` 条件（`ConditionStatus.CREATED = 0`）

## 固定执行流程（严格按顺序）

1. **输入校验**
   - `proposalId` 可转为非负整数
   - `bnbAddress` 是合法 EVM 地址
   - 若失败：返回 `stage=validation`

2. **链与账户校验**
   - 钱包已连接且当前地址等于 `bnbAddress`（忽略大小写）
   - 当前网络为 BSC Mainnet（56）
   - 检查原生 BNB 余额 `>= minBnbForGas`（默认 0.001）
   - 若失败：返回 `stage=wallet` 或 `stage=gas-check`

3. **解析提案地址**
   - 读取 `proposalAddress = Factory.proposals(proposalId)`
   - 校验 `proposalAddress` 非零且 `Factory.isProposal(proposalAddress) == true`
   - 若失败：返回 `stage=resolve-proposal`

4. **委员会成员检查**
   - `isMember = Factory.isProposalCommitteeMember(proposalAddress, bnbAddress)`
   - 若 `isMember=false`，进入第 5 步
   - 若 `isMember=true`，进入第 6 步

5. **自动最小质押加入委员会（仅非成员时）**
   - 读取 `minStake = Factory.getProposalCommitteeMinStakeToJoin(proposalAddress)`
   - 读取 DOGE 余额，要求 `balance >= minStake`
   - 读取 DOGE allowance（spender=factory）
   - 若 allowance 不足且 `approve=true`：先 `approve(factory, minStake)` 并等待确认
   - 调用 `Factory.stakeForProposalCommittee(proposalAddress, minStake)` 并等待确认
   - 再次校验 `isProposalCommitteeMember == true`
   - 任一步失败：返回 `stage=stake-committee`

6. **枚举 CREATED 条件**
   - `count = Proposal.conditionCount()`
   - 循环 `i=0..count-1`：
     - `condition = Proposal.conditionContracts(i)`
     - `status = Proposal.conditionStatus(condition)`
     - 仅收集 `status == 0`（CREATED）
   - 若一个都没有，返回成功并附加 warning：`no-created-conditions`

7. **逐条投票激活**
   - 对每个 `createdCondition` 调用：
     - `Proposal.voteOnConditionActivation(condition, true)`
   - 每笔交易等待确认
   - 若单条失败，记录到 `failures[]` 并继续下一条
   - 若全部失败：返回 `stage=activate-vote` + `ok=false`
   - 若部分成功：`ok=true` 且写入 `warnings`

8. **输出标准结果**
   - 返回结构化 JSON（见“输出契约”）

## 失败提示模板（环节达不到要求时必须提示）

- `validation`：`参数不合法：请提供有效 proposalId 与 bnbAddress（0x...）。`
- `wallet`：`钱包未连接或当前地址与 bnbAddress 不一致，请切换到指定地址后重试。`
- `gas-check`：`BNB 余额不足以支付 gas，至少需要 {minBnbForGas} BNB（建议更多）。`
- `resolve-proposal`：`无法解析提案：proposalId={proposalId} 对应提案不存在或无效。`
- `stake-committee`：`地址不是该提案委员会成员，且自动最小质押失败：{reason}`
- `approve`：`DOGE 授权失败，无法完成委员会质押。`
- `activate-vote`：`条件激活投票失败：{failedCount}/{totalCount} 条失败，请查看 failures 详情。`
- `confirm`：`交易未确认或超时，请检查链上状态后重试。`

## 输出契约

成功（全部成功或部分成功）：

```json
{
  "ok": true,
  "proposalId": 0,
  "proposalAddress": "0x...",
  "bnbAddress": "0x...",
  "committeeJoinedByStake": false,
  "stakeTxHash": "0x... or null",
  "createdConditionCount": 0,
  "attemptedConditionCount": 0,
  "successCount": 0,
  "failedCount": 0,
  "successes": [
    {
      "conditionAddress": "0x...",
      "txHash": "0x..."
    }
  ],
  "failures": [
    {
      "conditionAddress": "0x...",
      "error": "human readable reason"
    }
  ],
  "warnings": [
    "no-created-conditions",
    "partial-success"
  ],
  "nextActions": [
    "Refresh proposal conditions",
    "Check pending activation votes in committee page"
  ]
}
```

失败：

```json
{
  "ok": false,
  "stage": "validation|wallet|gas-check|resolve-proposal|stake-committee|approve|activate-vote|confirm",
  "error": "human readable reason",
  "retryable": true
}
```

## 实现建议（ethers/viem）

- 先读 Factory 地址（deployment 文件）和 ABI，再读 Proposal ABI。
- 任何金额统一按 1e18 精度处理，避免浮点。
- 批量激活建议逐条发交易并记录每条结果，不要“一笔失败全中断”。
- 对可预期错误给用户中文提示（余额不足、授权不足、非委员会成员、网络错误）。

## 安全边界

- 不使用私钥明文。
- 不绕过钱包确认。
- 不自动确认不可逆交易。
- 当 `approve=false` 且授权不足时，必须返回失败并提示用户先授权。

## 参考

- 本技能涉及的合约方法（自包含）：[references/CONTRACT_METHODS.md](references/CONTRACT_METHODS.md)
