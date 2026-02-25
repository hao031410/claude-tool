# claude-tool

面向 Claude / Codex / cc-switch 的 Skill 仓库。

## Skill 功能介绍

| Skill | 功能 | 路径 |
|---|---|---|
| `sql-generator` | 根据业务描述生成 SQL，并先校验表名/字段名/枚举值等约束 | `skills/sql-generator` |
| `terp-model-generator` | 根据字段定义生成 TERP 模型相关代码（如 PO） | `skills/terp-model-generator` |
| `dlna` | 发现 DLNA 设备并控制媒体播放（电视/音响等） | `skills/dlna` |
| `tutor` | 数学题一对一讲解，生成 HTML 讲义与配音 Manim 视频 | `skills/tutor` |
| `terminus-emp-skill` | EMP 工时填报：鉴权、项目校验、按比例写入、写后回查与统计 | `skills/terminus-emp-skill` |

## 仓库引入

### Claude

```bash
/plugin marketplace add hao031410/claude-tool
```

### cc-switch

在 skill marketplace 中添加仓库：`hao031410/claude-tool`
