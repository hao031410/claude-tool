---
name: skill-analysis
description: 评估所有 skill 并推荐合适的
argument-hint: [你的任务描述]
allowed-tools: ["Bash", "AskUserQuestion", "Skill"]
---

# Skill Analysis

分析用户任务，评估所有可用 skill（系统技能 + 本地技能），推荐并执行最合适的选择。

**触发条件**：

- 用户请求技能推荐（如 "用哪个 skill 合适"、"评估 skill"）
- 任务描述模糊，需要帮助用户选择合适的技能
- 用户明确请求评估技能匹配度

**不触发**：
- 用户已经明确指定使用哪个 skill（直接执行，不要再次推荐）
- 简单问题无需技能（如 "今天天气如何"）

## 获取任务描述

$IF($ARGUMENTS,
  **用户任务**：$ARGUMENTS
  ,
  使用 AskUserQuestion 询问用户要完成的任务，然后继续分析。

  **问题格式**：
  - question: "请描述你要完成的任务"
  - header: "任务描述"
  - options: 不提供选项，让用户自由输入
)

## 发现所有 Skill

### 1. 获取系统技能列表

系统技能已在对话上下文中提供，直接从 `<system-reminder>` 标签中提取可用技能列表。

### 2. 扫描本地技能

扫描项目技能目录获取本地技能：

```bash
# 扫描项目 skills 目录
find skills -name "SKILL.md" -maxdepth 2 2>/dev/null | while read f; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  echo "local:$name:$f"
done

# 扫描 ~/.claude/skills 用户技能
find ~/.claude/skills -name "SKILL.md" -maxdepth 2 2>/dev/null | while read f; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  echo "user:$name:$f"
done
```

### 3. 提取技能元数据

对每个发现的 SKILL.md 文件，读取前 30 行提取：
- `name` 字段（frontmatter）
- `description` 字段（frontmatter）
- 触发条件描述（body 中的 "This skill should be used when..." 或 "触发条件："）

## 评估 Skill 匹配度

对每个 skill 进行评分（0-10 分）：

**评分标准**：

| 维度 | 分值 | 说明 |
|------|------|------|
| 关键词匹配 | +3 | 任务描述包含 skill name/description 中的关键词 |
| 触发条件匹配 | +5 | 任务符合 "This skill should be used when..." 中的场景 |
| 项目上下文 | +2 | 如 jasolar 项目 → tsrm-developer；含 terminus/emp → terminus-emp-skill |
| 负向匹配 | -5 | 任务明确不符合 skill 适用范围 |
| 用户指定 | +10 | 用户明确要求使用某个 skill（直接执行，跳过评估） |

**优先级规则**：
1. 用户明确指定的 skill → 直接执行，不评估
2. 系统技能 > 本地技能（系统技能更稳定、文档更完善）
3. 专用技能 > 通用技能（如 `sql-generator` > `code-review`）

按得分排序，筛选 **TOP 3-5 个 skill**。

## 输出推荐结果

显示推荐的 skill 表格：

```
## 推荐的 Skill（按匹配度排序）

| Skill | 来源 | 推荐理由 | 适用场景 |
|-------|------|----------|----------|
| skill-name-1 | 系统 | 得分 9/10：匹配关键词 X、Y | 适用场景描述 |
| skill-name-2 | 本地 | 得分 7/10：符合触发条件 | 适用场景描述 |
| skill-name-3 | 用户 | 得分 5/10：部分匹配 | 适用场景描述 |

其他 [N] 个 skill 不匹配此任务。
```

**来源标识**：
- `系统` - 内置技能（everything-claude-code:*, document-skills:*, superpowers:*）
- `本地` - 项目 skills 目录下的技能
- `用户` - ~/.claude/skills 用户技能

## 用户选择

使用 AskUserQuestion 让用户选择要执行的 skill：

**参数设置**：
- question: "请选择最适合的 skill 来执行此任务"
- header: "选择 Skill"
- options: 列出推荐的 3-5 个 skill（label=skill name, description=推荐理由 + 适用场景）
- multiSelect: false

**选项顺序**：按匹配度得分降序排列，最高分的放在第一个。

## 执行选中的 Skill

用户选择后，使用 Skill tool 执行选中的 skill：

**Skill 参数**：
- skill: 用户选择的 skill name
- args: 用户的原始任务描述（$ARGUMENTS 或询问获取的描述）

**执行失败处理**：
- Skill 不存在 → 提示用户并重新推荐
- Skill 需要额外参数 → 使用 AskUserQuestion 补充询问
- Skill 执行报错 → 显示错误信息，提供替代方案

---

## 边界情况处理

1. **没有 $ARGUMENTS**：先询问任务描述再评估
2. **没有明确匹配**：列出得分最高的 3 个供用户选择
3. **所有 skill 都不匹配**：提示用户"没有找到匹配的 skill，请描述更具体的任务"
4. **用户选择 Other**：询问用户想输入什么，然后重新评估或直接执行
5. **用户已指定 skill**：直接执行，跳过评估流程
6. **任务过于简单**：如"你好"、"帮助"，直接回复，不触发技能评估

## 性能优化

1. **缓存技能列表**：首次扫描后缓存技能元数据，避免重复读取文件
2. **懒加载技能详情**：只对 TOP 10 技能读取完整 SKILL.md 内容
3. **并行处理**：并发读取多个 SKILL.md 文件内容
