# claude-tool

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Plugin](https://img.shields.io/badge/plugin-marketplace-green.svg)](https://github.com/hao031410/claude-tool)

**面向特定场景的 Claude Code 技能模块库，提供开箱即用的开发工具链。**

[English](README_EN.md) | 简体中文

---

## Quick Start

### 安装

```bash
# Claude Code
/plugin marketplace add hao031410/claude-tool
```

验证安装：
```bash
skill-check
```

---

## Skills Overview

### 🚀 Development Productivity

| Skill | Description | Docs |
|-------|-------------|------|
| `git-commit` | 智能 Git 提交，支持 emoji、自动拆分、预览模式 | [SKILL.md](skills/git-commit/SKILL.md) |
| `technical-docs` | 技术文档生成：README、API 文档、架构文档 | [SKILL.md](skills/technical-docs/SKILL.md) |

### 💼 Business Development

| Skill | Description | Docs |
|-------|-------------|------|
| `sql-generator` | SQL 查询生成，自动验证表名/字段名/枚举值 | [SKILL.md](skills/sql-generator/SKILL.md) |
| `terminus-emp-skill` | EMP 工时填报自动化 | [SKILL.md](skills/terminus-emp-skill/SKILL.md) |

### 🎬 Multimedia Tools

| Skill | Description | Docs |
|-------|-------------|------|
| `tutor` | 数学教学视频制作 (Manim 动画) | [SKILL.md](skills/tutor/SKILL.md) |
| `dlna` | DLNA 媒体控制（电视/音响） | [SKILL.md](skills/dlna/SKILL.md) |

---

## MCP Tools

独立运行的 MCP Server 工具，通过 bunx 安装使用。

| Tool | Description | Docs |
|------|-------------|------|
| `image-recognizer` | 图片识别 MCP Server，支持剪贴板/文件/URL 输入 | [README.md](mcp/image-recognizer/README.md) |

### image-recognizer 使用示例

```bash
# 安装使用
bunx -y @bytego/image-recognizer@latest

# 查看帮助
image-recognizer -h
```

Claude Code 配置：
```json
{
  "mcpServers": {
    "image-recognizer": {
      "command": "bunx",
      "args": ["-y", "@bytego/image-recognizer@latest"],
      "env": {
        "VISION_API_URL": "https://api.openai.com/v1/chat/completions",
        "VISION_API_KEY": "your-api-key",
        "VISION_MODEL": "gpt-4o"
      }
    }
  }
}
```

---

## Repository Structure

```
claude-tool/
├── .claude-plugin/        # 插件市场配置
├── commands/              # Claude Code 命令定义
├── hooks/                 # 钩子脚本
├── mcp/                   # MCP Server 工具
│   └── image-recognizer/  # 图片识别工具
├── prompts/               # 提示词模板
└── skills/                # 技能模块
```

---

## Development

### Python Skill Dependencies

```bash
uv pip install -r requirements.txt
```

### MCP Tool Development

```bash
cd mcp/image-recognizer
bun install
bun run index.ts -v
```

---

## Documentation

- [CLAUDE.md](CLAUDE.md) - 项目概述（供 AI 理解）
- [skills/*/SKILL.md](skills/) - 技能详细规范
- [mcp/*/README.md](mcp/) - MCP 工具使用文档

---

## License

MIT License - See [LICENSE](LICENSE) for details.
