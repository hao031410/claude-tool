# CLAUDE.md

Claude Code Skill 仓库，提供多个面向特定场景的技能模块。

## 仓库结构

```
claude-tool/
├── .claude-plugin/        # 插件市场配置
├── commands/              # Claude Code 命令定义
├── hooks/                 # 钩子脚本
├── mcp/                   # MCP Server 工具
│   └── image-recognizer/  # 图片识别 MCP Server
├── prompts/               # 提示词模板
└── skills/                # 技能模块
```

## Skills 目录

| Skill | 功能 | 入口文件 |
|-------|------|----------|
| `sql-generator` | SQL 查询生成，自动验证表名/字段名 | `skills/sql-generator/SKILL.md` |
| `git-commit` | 智能 Git 提交，支持 emoji、自动拆分 | `skills/git-commit/SKILL.md` |
| `technical-docs` | 技术文档生成引擎 | `skills/technical-docs/SKILL.md` |
| `tutor` | 数学教学视频制作 (Manim) | `skills/tutor/SKILL.md` |
| `dlna` | DLNA 媁体控制 | `skills/dlna/SKILL.md` |
| `terminus-emp-skill` | EMP 工时填报 | `skills/terminus-emp-skill/SKILL.md` |

## MCP 工具

| 工具 | 功能 | 入口文件 |
|------|------|----------|
| `image-recognizer` | 图片识别 MCP Server | `mcp/image-recognizer/README.md` |

## 架构要点

- Skills 通过 `SKILL.md` 定义规范，references/ 存放参考文档
- MCP 工具通过 bunx 运行，配置在 Claude Code settings.json
- hooks/preToolUse.js 提供危险命令拦截