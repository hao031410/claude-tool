---
description: 评估所有 skill 并推荐合适的
argument-hint: [你的任务描述]
allowed-tools: ["Bash", "AskUserQuestion", "Skill"]
---

# Skill 评估命令

分析用户任务，评估所有可用 skill，推荐最合适的选择。

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

扫描 skill 目录获取完整列表：

```bash
find ~/.claude/skills -name "SKILL.md" -exec sh -c 'echo "$(dirname {} | xargs basename):{}"' \; 2>/dev/null

find ~/.claude/plugins -path "*/skills/*/SKILL.md" -exec sh -c 'd=$(dirname {}); ancestor=$(dirname $(dirname $d)); echo "$(basename $d):$(basename $ancestor):{}"' \; 2>/dev/null | head -20
```

对每个发现的 SKILL.md 文件，读取前 30 行提取：
- `name` 字段（frontmatter）
- `description` 字段（frontmatter）
- 触发条件描述（body 中的 "This skill should be used when..." 或 "触发条件："）

## 评估 Skill 匹配度

对每个 skill 进行评分（0-10 分）：

**评分标准**：
1. **关键词匹配**（+3 分）：任务描述包含 skill name 中的关键词
2. **触发条件匹配**（+5 分）：任务符合 "This skill should be used when..." 中的场景
3. **项目上下文**（+2 分）：如 jasolar 项目 → tsrm-developer
4. **负向匹配**（-5 分）：任务明确不符合 skill 适用范围

按得分排序，筛选 **TOP 3-5 个 skill**。

## 输出推荐结果

显示推荐的 skill 表格：

```
## 推荐的 Skill（按匹配度排序）

| Skill | 推荐理由 | 适用场景 |
|-------|----------|----------|
| skill-name-1 | 得分 9/10：匹配关键词 X、Y | 适用场景描述 |
| skill-name-2 | 得分 7/10：符合触发条件 | 适用场景描述 |
| skill-name-3 | 得分 5/10：部分匹配 | 适用场景描述 |

其他 [N] 个 skill 不匹配此任务。
```

## 用户选择

使用 AskUserQuestion 让用户选择要执行的 skill：

**参数设置**：
- question: "请选择最适合的 skill 来执行此任务"
- header: "选择 Skill"
- options: 列出推荐的 3-5 个 skill（label=skill name, description=推荐理由）
- multiSelect: false

## 执行选中的 Skill

用户选择后，使用 Skill tool 执行选中的 skill：

**Skill 参数**：
- skill: 用户选择的 skill name
- args: 用户的原始任务描述（$ARGUMENTS 或询问获取的描述）

---

## 边界情况处理

1. **没有 $ARGUMENTS**：先询问任务描述再评估
2. **没有明确匹配**：列出得分最高的 3 个供用户选择
3. **所有 skill 都不匹配**：提示用户"没有找到匹配的 skill，请描述更具体的任务"
4. **用户选择 Other**：询问用户想输入什么，然后重新评估或直接执行
