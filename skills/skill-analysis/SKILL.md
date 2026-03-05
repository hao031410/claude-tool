---
name: skill-analysis
description: 使用当任务描述模糊、不确定使用哪个技能合适时，仅列出推荐技能（不执行选择）。
argument-hint: [你的任务描述]
allowed-tools: ["Bash", "AskUserQuestion"]
---

# Skill Analysis

分析用户任务，评估所有可用 skill（系统技能 + 本地技能 + 用户技能），推荐最适合的选择。

## 触发条件

**使用此技能当**：
- 任务描述模糊，不确定使用哪个技能合适
- 需要帮助选择/评估技能匹配度
- 用户请求技能推荐（如 "用哪个 skill 合适"、"评估 skill"）

**不使用此技能当**：
- 用户已明确指定使用哪个 skill → 直接执行
- 简单问题无需技能（如问候、问答）

## 执行流程

### 1. 获取任务描述

- 有 `$ARGUMENTS` → 直接使用
- 无 `$ARGUMENTS` 或描述模糊 → 使用 `AskUserQuestion` 确认任务细节

### 2. 发现所有技能

**系统技能**：从 `<system-reminder>` 标签中提取

**本地技能**：扫描 `skills/` 目录

**用户技能**：扫描 `~/.claude/skills/`

### 3. 评估匹配度

评分维度（0-10 分）：

| 维度 | 分值 | 说明 |
|------|------|------|
| 触发条件匹配 | +5 | 任务符合 skill description 中的使用场景 |
| 关键词匹配 | +3 | 任务描述包含 skill name/description 关键词 |
| 项目上下文 | +2 | 如 jasolar 项目 → tsrm-developer |

**筛选规则**：
- 得分 ≥ 7 分：强烈推荐
- 得分 4-6 分：推荐
- 得分 < 4 分：不推荐

**优先级**：系统技能 > 本地技能 > 用户技能；专用技能 > 通用技能

### 4. 输出推荐结果

输出推荐表格后 **结束**：

```markdown
## 推荐的 Skill

| Skill | 来源 | 得分 | 推荐理由 |
|-------|------|------|----------|
| skill-name-1 | 系统 | 9/10 | 匹配触发条件 X、Y |
| skill-name-2 | 本地 | 6/10 | 符合项目上下文 |
```

**后续触发方式**：用户自行触发

---

## 完整示例

**用户输入**：`/skill-check 我想给项目添加端到端测试`

**步骤 1：获取任务描述** → 已有 `$ARGUMENTS`

**步骤 2：发现技能** → 系统技能列表 + 本地扫描

**步骤 3：评估匹配度**：
- `everything-claude-code:e2e`：触发条件匹配 (+5) + 关键词匹配 (+3) = **8/10**
- `everything-claude-code:tdd`：关键词匹配 (+3) = **3/10**
- `everything-claude-code:code-reviewer`：关键词匹配 (+2) = **2/10**

**步骤 4：输出推荐**（结束）：
```markdown
## 推荐的 Skill

| Skill | 来源 | 得分 | 推荐理由 |
|-------|------|------|----------|
| everything-claude-code:e2e | 系统 | 8/10 | 专为 E2E 测试设计，使用 Playwright |
| everything-claude-code:tdd | 系统 | 3/10 | 通用测试流程，非 E2E 专用 |
```

**步骤 5：用户自行触发**
