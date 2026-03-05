# claude-tool

Claude Code Skill 仓库，提供多个面向特定场景的技能模块。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Plugin](https://img.shields.io/badge/plugin-marketplace-green.svg)](https://github.com/hao031410/claude-tool)

## 快速开始

### 安装方式

| 平台 | 安装命令 |
|------|---------|
| **Claude** | `/plugin marketplace add hao031410/claude-tool` |
| **cc-switch** | 在 skill marketplace 中添加仓库：`hao031410/claude-tool` |

### 使用技能

```bash
# 查看可用技能
/skill-check

# 使用特定技能
skill <skill-name> [arguments]
```

## 技能列表

### 开发效率

| Skill | 功能 | 触发场景 |
|-------|------|----------|
| `git-commit` | 智能 git 提交创建，支持 emoji、自动拆分、预览模式 | 创建 git 提交时 |
| `technical-docs` | 完整的技术文档系统，支持 README/API/架构/运行手册 | 编写技术文档时 |
| `skill-analysis` | 分析任务并推荐最合适的技能 | 不确定使用哪个技能时 |

### 业务开发

| Skill | 功能 | 触发场景 |
|-------|------|----------|
| `sql-generator` | 根据业务描述生成 SQL，自动验证表名/字段名/枚举值 | 编写数据库查询时 |
| `terp-model-generator` | 根据字段定义生成 TERP 模型代码 (PO/DTO/Repo/Converter) | 生成实体模型代码时 |
| `terminus-emp-skill` | EMP 工时填报：鉴权、项目校验、按比例写入、统计 | 填工时/工时统计时 |

### 多媒体工具

| Skill | 功能 | 触发场景 |
|-------|------|----------|
| `dlna` | 发现 DLNA 设备并控制媒体播放（电视/音响） | 控制媒体设备播放时 |
| `tutor` | 数学题讲解，生成 HTML 讲义与 Manim 动画视频 | 数学题教学/生成讲解视频时 |

## 技能详细介绍

### sql-generator

**工作流程：**
1. 搜索 PO 类获取真实表名 (`@TableName`) 和字段映射 (`@TableField`)
2. 确认约束条件（表名、字段名、枚举值）
3. 展示 SQL 计划并确认
4. 选择模板生成 SQL (orphan-records / data-diff / aggregation)
5. 同步文档到 `.claude/doc/sql-generator/`

**查询模板：**
- `orphan-records` - 查找 A 表有但 B 表没有的记录
- `data-diff` - 对比两表差异
- `missing-relations` - 缺失关联检查
- `bidirectional-check` - 双向关联检查
- `count-aggregation` - 分组聚合统计

详见：[skills/sql-generator/SKILL.md](skills/sql-generator/SKILL.md)

---

### terp-model-generator

**生成文件：**
- **PO** - Persistent Object (MyBatis Plus 实体)
- **DTO** - Data Transfer Object
- **Dict** - 枚举字典接口（针对 ENUM 字段）
- **Repo** - Repository 接口
- **Converter** - MapStruct 转换器

**DDD 分层架构：**
```
{project}-spi/
├── model/{module}/
│   ├── po/        # Persistent Object
│   ├── dto/       # Data Transfer Object
│   └── req/       # Request Object
├── dict/{module}/ # 枚举字典接口
└── convert/       # MapStruct Converter

{project}-infrastructure/
└── repo/{module}/ # Repository 接口
```

详见：[skills/terp-model-generator/SKILL.md](skills/terp-model-generator/SKILL.md)

---

### tutor

**8 步工作流：**
1. 数学分析 → 2. HTML 可视化 → 3. 分镜脚本 → 4. TTS 音频 →
5. 验证更新 → 6. 脚手架 → 7. 代码实现 → 8. 渲染验证

**输出产物：**
- HTML 讲解文档（含 SVG 图形和画图过程）
- 分镜脚本（含画面/字幕/读白/动画设计）
- TTS 配音音频文件
- Manim 动画视频（带字幕和高亮同步）

详见：[skills/tutor/SKILL.md](skills/tutor/SKILL.md)

---

### dlna

**快速开始：**
```bash
# 发现设备
uv run dlna discover

# 设置默认设备
uv run dlna config --device "HT-Z9F"

# 播放媒体
uv run dlna play "http://example.com/video.mp4"

# 停止播放
uv run dlna stop
```

**支持设备：**
- 智能电视（Sony、Samsung、LG 等）
- 支持 DLNA 的音响/功放
- 任何 UPnP MediaRenderer 设备

详见：[skills/dlna/SKILL.md](skills/dlna/SKILL.md)

---

### terminus-emp-skill

**执行顺序：**
1. 加载缓存 → 2. 参数校验 → 3. 拉项目清单 → 4. 用户确认 →
5. 执行写入 → 6. 写后回查 → 7. 统计输出

**执行原则：**
- 优先必要参数校验，再执行脚本
- 未展示项目清单前，禁止要求用户直接提供 `projectCode/detailCode`
- 写入前必须校验配置完整且 percentage 合计为 1.0
- 写入失败时只通知原因，由用户自行决定后续操作

详见：[skills/terminus-emp-skill/SKILL.md](skills/terminus-emp-skill/SKILL.md)

---

### git-commit

**提交类型与 Emoji：**

| Type | Emoji | 描述 |
|------|-------|------|
| `feat` | ✨ | 新功能 |
| `fix` | 🐛 | Bug 修复 |
| `docs` | 📝 | 文档 |
| `refactor` | ♻️ | 重构 |
| `test` | ✅ | 测试 |
| `chore` | 🔧 | 构建/工具 |

**使用示例：**
```bash
# 预览提交计划（推荐先使用）
skill git-commit -d

# 执行提交
skill git-commit

# 提交并推送
skill git-commit -p

# 英文提交消息
skill git-commit -e
```

详见：[skills/git-commit/SKILL.md](skills/git-commit/SKILL.md)

---

### skill-analysis

**触发条件：**
- 用户请求技能推荐（如 "用哪个 skill 合适"）
- 任务描述模糊，需要帮助选择合适的技能

**评分维度：**
- 关键词匹配 (+3)
- 触发条件匹配 (+5)
- 项目上下文 (+2)
- 负向匹配 (-5)

详见：[skills/skill-analysis/SKILL.md](skills/skill-analysis/SKILL.md)

---

### technical-docs

**文档类型：**
- README
- Getting Started Guide
- API Reference
- Architecture Document
- Runbook
- CONTRIBUTING.md
- Changelog

**质量评分维度（100 分制）：**
- Accuracy (20 分) - 技术准确性
- Completeness (15 分) - 内容完整性
- Clarity (15 分) - 表述清晰度
- Structure (15 分) - 结构合理性
- Examples (15 分) - 示例完整性
- Maintainability (10 分) - 可维护性
- Searchability (5 分) - 可搜索性
- Accessibility (5 分) - 可访问性

详见：[skills/technical-docs/SKILL.md](skills/technical-docs/SKILL.md)

## 仓库结构

```
claude-tool/
├── .claude-plugin/        # 插件市场配置
├── commands/              # Claude Code 命令定义
│   └── skill-check.md     # 技能评估与推荐
├── hooks/                 # 钩子脚本
│   └── preToolUse.js      # 危险命令拦截
├── prompts/               # 提示词模板
├── rules/                 # 编码规范
└── skills/                # 技能模块
    ├── sql-generator/     # SQL 生成工具
    ├── terp-model-generator/  # TERP 模型代码生成
    ├── tutor/             # 数学教学视频制作 (Manim)
    ├── dlna/              # DLNA 媒体控制
    ├── terminus-emp-skill/  # EMP 工时填报
    ├── skill-analysis/    # 技能评估推荐
    ├── technical-docs/    # 技术文档引擎
    └── git-commit/        # Git 提交助手
```

## 开发环境

### Python 依赖管理

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
uv run dlna discover    # 发现设备
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

**禁止的命令：**
- `rm -rf /`
- `dd` 覆盖磁盘
- `mkfs` 格式化
- `kill -9 -1`

**需要确认的命令：**
- `git reset/rebase`
- `rm`
- `docker rm/rmi`
- `kubectl delete`

## 相关文档

- [CLAUDE.md](CLAUDE.md) - 项目详细指南和架构说明
- [skills/*/SKILL.md](skills/) - 各技能详细规范
- [skills/*/references/](skills/) - 技术参考文档

## 许可证

MIT License - 详见 [LICENSE](LICENSE)
