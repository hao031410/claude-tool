# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Code Skill 仓库，提供多个面向特定场景的技能模块。

## 仓库结构

```
claude-tool/
├── .claude-plugin/        # 插件市场配置
├── commands/              # Claude Code 命令定义
├── hooks/                 # 钩子脚本 (preToolUse.js - 危险命令拦截)
├── prompts/               # 提示词模板
└── skills/                # 技能模块
    ├── sql-generator/     # SQL 生成工具
    ├── tutor/             # 数学教学视频制作 (Manim)
    ├── dlna/              # DLNA 媒体控制
    └── terminus-emp-skill/  # EMP 工时填报
```

## Skills 介绍

| Skill | 功能 | 入口 |
|-------|------|------|
| `sql-generator` | 根据业务描述生成 SQL，先验证表名/字段名/枚举值 | SKILL.md |
| `dlna` | 发现 DLNA 设备并控制媒体播放（电视/音响） | SKILL.md, README.md |
| `tutor` | 数学题讲解，生成 HTML 讲义与 Manim 动画视频 | SKILL.md, README.md |
| `terminus-emp-skill` | EMP 工时填报：鉴权、项目校验、按比例写入、统计 | SKILL.md, references/spec.md |

## 开发环境

### Python 技能依赖管理

使用 `uv` 管理依赖：

```bash
# 安装依赖
uv pip install -r requirements.txt

# 创建虚拟环境
uv venv .venv
source .venv/bin/activate
```

### DLNA 技能

```bash
cd skills/dlna
uv pip install -e .
uv run dlna discover  # 发现设备
uv run dlna play "<url>"  # 播放媒体
```

### Tutor 技能

```bash
cd skills/tutor
uv pip install -r requirements.txt
# 工作流：数学分析 → HTML 可视化 → 分镜脚本 → TTS 音频 → 渲染
```

## 钩子配置

`hooks/preToolUse.js` - 危险命令拦截脚本，在 bypass 模式下提供安全防护：

- **禁止的命令**：`rm -rf /`、`dd` 覆盖磁盘、`mkfs` 格式化、`kill -9 -1` 等
- **需要确认的命令**：`git reset/rebase`、`rm`、`docker rm/rmi`、`kubectl delete` 等

## 命令定义

- `commands/skill-check.md` - 评估所有 skill 并推荐合适的技能

## 架构模式

### sql-generator

工作流程：
1. 搜索 PO 类获取真实表名 (`@TableName`) 和字段映射 (`@TableField`)
2. 确认约束条件（表名、字段名、枚举值）
3. 展示 SQL 计划并确认
4. 选择模板生成 SQL (orphan-records / data-diff / aggregation)
5. 同步文档到 `.claude/doc/sql-generator/`

### tutor

8 步工作流：
1. 数学分析 → 2. HTML 可视化 → 3. 分镜脚本 → 4. TTS 音频 →
5. 验证更新 → 6. 脚手架 → 7. 代码实现 → 8. 渲染验证

### terminus-emp-skill

执行顺序：
1. 加载缓存 → 2. 参数校验 → 3. 拉项目清单 → 4. 用户确认 →
5. 执行写入 → 6. 写后回查 → 7. 统计输出

## 相关文档

- README.md - 仓库整体介绍和插件安装方式
- 各 skill 目录下的 SKILL.md - 详细技能规范
- 各 skill 目录下的 references/ - 技术参考文档
