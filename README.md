# claude-tool

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Plugin](https://img.shields.io/badge/plugin-marketplace-green.svg)](https://github.com/hao031410/claude-tool)
[![Skills](https://img.shields.io/badge/skills-8-blue.svg)](skills/)

**面向特定场景的 Claude Code 技能模块库，提供开箱即用的开发工具链。**

[English](README_EN.md) | 简体中文

---

## Quick Start

### 安装

```bash
# Claude Code
/plugin marketplace add hao031410/claude-tool

# cc-switch
# 在 skill marketplace 中添加仓库：hao031410/claude-tool
```

验证安装：
```bash
skill-check
```

预期输出：
```
✅ 发现 8 个技能：
  - git-commit        智能 Git 提交助手
  - sql-generator     SQL 查询生成器
  - ...
```

### 第一次使用

```bash
# 查看推荐技能
skill-check "我要生成 SQL 查询"

# 使用特定技能
skill sql-generator 查找所有没有订单的用户
```

---

## What It Does

**解决开发过程中的重复性工作：**

- ✨ **智能提交** - 自动生成符合规范的 commit message，支持自动拆分、预览模式
- 🗄️ **SQL 生成** - 根据业务描述生成可执行 SQL，自动验证表名/字段名
- 🏗️ **代码生成** - 从字段定义生成完整的 DDD 模型层代码
- 📊 **工时填报** - 自动化 EMP 工时填报和统计
- 📝 **技术文档** - 从代码生成高质量技术文档
- 🎬 **教学视频** - 数学题讲解动画视频自动生成
- 📺 **媒体控制** - DLNA 设备发现和媒体播放控制

**适用于：**
- 需要频繁编写 SQL 查询的后端开发者
- 使用 Trantor2 框架的团队
- 重视代码规范和提交历史的团队
- 需要自动化技术文档的项目
- 制作技术教学内容的创作者

---

## Skills Overview

### 🚀 Development Productivity

| Skill | Description | When to Use |
|-------|-------------|-------------|
| `git-commit` | Intelligent Git commits with emoji, auto-split, dry-run, and auto-push | Creating git commits |
| `technical-docs` | Complete documentation system: README, API docs, architecture, runbooks | Writing technical documentation |
| `skill-analysis` | Analyze tasks and recommend best-fit skills | Unsure which skill to use |

### 💼 Business Development

| Skill | Description | When to Use |
|-------|-------------|-------------|
| `sql-generator` | Generate executable SQL with table/field/enum validation | Writing database queries |
| `terp-developer` | Trantor2 framework development assistant: model transformation, impact analysis, architecture guidance | Working with Trantor2 framework |
| `terminus-emp-skill` | EMP timesheet automation: auth, project validation, proportional entry, statistics | Filling timesheets |

### 🎬 Multimedia Tools

| Skill | Description | When to Use |
|-------|-------------|-------------|
| `dlna` | Discover DLNA devices and control media playback (TV/speakers) | Controlling media devices |
| `tutor` | Math tutorial generation: HTML handouts & Manim animation videos | Creating math tutorial videos |

---

## Detailed Features

### sql-generator

**Workflow:**
1. Search PO classes to get real table names (`@TableName`) and field mappings (`@TableField`)
2. Verify constraints (table names, field names, enum values)
3. Display SQL plan and confirm
4. Select template to generate SQL (orphan-records / data-diff / aggregation)
5. Sync documentation to `.claude/doc/sql-generator/`

**Query Templates:**
- `orphan-records` - Find records in A but not in B
- `data-diff` - Compare differences between two tables
- `missing-relations` - Check missing relations
- `bidirectional-check` - Bidirectional relation check
- `count-aggregation` - Group aggregation statistics

📖 [Full Documentation](skills/sql-generator/SKILL.md)

---

### terp-developer

**Core Capabilities:**
- **Model Transformation** - Bidirectional conversion (PO ↔ JSON)
- **Impact Analysis** - Full-chain dependency tracking
- **Semantic Conflict Detection** - Detect field type/meaning changes
- **Architecture Guidance** - Layer responsibility and pattern recommendations
- **Code Standards Fix** - Collection null checks, repository patterns
- **Knowledge Base** - Cross-session memory for external models

**Smart Routing:**
```bash
# Initialize project
/terp-developer -init

# Create model from JSON
/terp-developer 创建 SettAccountPO

# Export model to JSON
/terp-developer 将 SettDocTrPO 导出为 JSON

# Architecture consultation
/terp-developer 结算单创建逻辑应该放在哪层？

# Code fix
/terp-developer 修复 SettItemTrService 的集合判空问题
```

📖 [Full Documentation](skills/terp-developer/SKILL.md)

---

### tutor

**8-Step Workflow:**
1. Math Analysis → 2. HTML Visualization → 3. Storyboard → 4. TTS Audio →
5. Validation Update → 6. Scaffolding → 7. Code Implementation → 8. Render Verification

**Output Artifacts:**
- HTML tutorial document (with SVG graphics and drawing process)
- Storyboard script (with scenes/subtitles/narration/animation design)
- TTS voiceover audio files
- Manim animation videos (with synchronized subtitles and highlights)

📖 [Full Documentation](skills/tutor/SKILL.md)

---

### dlna

**Quick Start:**
```bash
# Discover devices
cd skills/dlna
uv run dlna discover

# Set default device
uv run dlna config --device "HT-Z9F"

# Play media
uv run dlna play "http://example.com/video.mp4"

# Stop playback
uv run dlna stop
```

**Supported Devices:**
- Smart TVs (Sony, Samsung, LG, etc.)
- DLNA-enabled speakers/receivers
- Any UPnP MediaRenderer device

📖 [Full Documentation](skills/dlna/SKILL.md)

---

### terminus-emp-skill

**Execution Order:**
1. Load cache → 2. Validate parameters → 3. Fetch project list → 4. User confirmation →
5. Execute write → 6. Verify write → 7. Output statistics

**Execution Principles:**
- Validate required parameters first, then execute scripts
- Never request `projectCode/detailCode` directly before showing project list
- Must validate complete configuration and percentage sum equals 1.0 before writing
- Only notify reason on write failure, let user decide next action

📖 [Full Documentation](skills/terminus-emp-skill/SKILL.md)

---

### git-commit

**Commit Types & Emoji:**

| Type | Emoji | Description |
|------|-------|-------------|
| `feat` | ✨ | New feature |
| `fix` | 🐛 | Bug fix |
| `docs` | 📝 | Documentation |
| `refactor` | ♻️ | Refactoring |
| `test` | ✅ | Testing |
| `chore` | 🔧 | Build/tooling |
| `remove` | 🔥 | Removal |
| `build` | 📦 | Dependency management |
| `ci` | 👷 | CI/CD |
| `config` | ⚙️ | Configuration |

**Usage Examples:**
```bash
# Preview commit plan (recommended first)
skill git-commit -d

# Execute commit
skill git-commit

# Commit and push
skill git-commit -p

# English commit messages
skill git-commit -e
```

📖 [Full Documentation](skills/git-commit/SKILL.md)

---

### skill-analysis

**Trigger Conditions:**
- User requests skill recommendation (e.g., "Which skill should I use")
- Task description is ambiguous, need help choosing appropriate skill

**Scoring Dimensions:**
- Keyword match (+3)
- Trigger condition match (+5)
- Project context (+2)
- Negative match (-5)

📖 [Full Documentation](skills/skill-analysis/SKILL.md)

---

### technical-docs

**Document Types:**
- README
- Getting Started Guide
- API Reference
- Architecture Document
- Runbook
- CONTRIBUTING.md
- Changelog

**Quality Scoring (100 points):**
- Accuracy (20 pts) - Technical correctness
- Completeness (15 pts) - Content completeness
- Clarity (15 pts) - Expression clarity
- Structure (15 pts) - Structural organization
- Examples (15 pts) - Example completeness
- Maintainability (10 pts) - Maintainability
- Searchability (5 pts) - Searchability
- Accessibility (5 pts) - Accessibility

📖 [Full Documentation](skills/technical-docs/SKILL.md)

---

## Repository Structure

```
claude-tool/
├── .claude-plugin/        # Plugin marketplace config
├── commands/              # Claude Code command definitions
│   └── skill-check.md     # Skill evaluation and recommendation
├── hooks/                 # Hook scripts
│   └── preToolUse.js      # Dangerous command interception
├── prompts/               # Prompt templates
├── skills/                # Skill modules
│   ├── sql-generator/     # SQL generation tool
│   ├── terp-developer/    # Trantor2 development assistant
│   ├── tutor/             # Math tutorial video creation (Manim)
│   ├── dlna/              # DLNA media control
│   ├── terminus-emp-skill/  # EMP timesheet filling
│   ├── skill-analysis/    # Skill evaluation and recommendation
│   ├── technical-docs/    # Technical documentation engine
│   └── git-commit/        # Git commit assistant
└── README*.md             # Documentation (Chinese/English)
```

---

## Development

### Python Dependency Management

Using `uv` for dependency management:

```bash
# Install dependencies
uv pip install -r requirements.txt

# Create virtual environment
uv venv .venv
source .venv/bin/activate
```

### DLNA Skill

```bash
cd skills/dlna
uv pip install -e .
uv run dlna discover    # Discover devices
uv run dlna play "<url>"  # Play media
```

### Tutor Skill

```bash
cd skills/tutor
uv pip install -r requirements.txt
# Workflow: Math analysis → HTML visualization → Storyboard → TTS audio → Render
```

---

## Hooks Configuration

`hooks/preToolUse.js` - Dangerous command interception script, providing safety protection in bypass mode:

**Blocked Commands:**
- `rm -rf /`
- `dd` disk overwrite
- `mkfs` formatting
- `kill -9 -1`

**Commands Requiring Confirmation:**
- `git reset/rebase`
- `rm`
- `docker rm/rmi`
- `kubectl delete`

---

## Documentation

- [CLAUDE.md](CLAUDE.md) - Project guidelines and architecture
- [skills/*/SKILL.md](skills/) - Detailed skill specifications
- [skills/*/references/](skills/) - Technical reference documents

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes using `skill git-commit`
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

Built with ❤️ for the Claude Code community. Special thanks to all contributors who make this project better.