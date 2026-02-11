# claude-tool

面向 Claude/cc-switch 的 Skill 仓库，当前提供两类能力：
1. `sql-generator`：业务 SQL 生成与约束校验
2. `terp-model-generator`：TERP 模型层代码生成（PO/DTO/Repository/Converter）

## Skills

| Skill | 适用场景 | 路径 |
|---|---|---|
| sql-generator | 根据业务问题生成 SQL，先校验表名/字段名/枚举值再输出查询 | `skills/sql-generator` |
| terp-model-generator | 根据字段定义或 JSON 生成 TERP 模型代码，先探测项目包结构 | `skills/terp-model-generator` |

## Marketplace 配置

仓库使用 `./.claude-plugin/marketplace.json` 声明插件入口，当前按 skill 拆分为两个独立插件：
1. `sql-generator` -> `./skills/sql-generator`
2. `terp-model-generator` -> `./skills/terp-model-generator`

## 安装（Claude）

1. 添加 marketplace（仓库）：
```bash
/plugin marketplace add hao031410/claude-tool
```
2. 安装插件：
```bash
/plugin install sql-generator@claude-tool
/plugin install terp-model-generator@claude-tool
```

## 安装（cc-switch）

1. 在 skill marketplace 中添加仓库：`hao031410/claude-tool`
2. 刷新并安装 `sql-generator` 或 `terp-model-generator`
3. 在目标应用（Claude/Codex）中启用对应 skill

## 快速验证

1. 仓库结构检查：
```bash
test -f .claude-plugin/marketplace.json && echo "marketplace ok"
test -f skills/sql-generator/SKILL.md && echo "sql skill ok"
test -f skills/terp-model-generator/SKILL.md && echo "terp skill ok"
```
2. JSON 合法性检查：
```bash
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null && echo "json ok"
```

## 常见问题

1. marketplace 添加后显示 404：确认仓库是公开仓库，且分支存在 `.claude-plugin/marketplace.json`。
2. 能拉到仓库但识别不到 skill：确认 `plugins[].source` 指向目录下存在 `SKILL.md`。
3. 改了内容未生效：在 cc-switch 中刷新仓库或重新安装对应 skill。

## 开发与维护

1. 修改 skill 内容请直接编辑 `skills/*/SKILL.md` 与其 `references/`
2. 新增 skill 时，在 `skills/<new-skill>/SKILL.md` 创建后，同步更新 `./.claude-plugin/marketplace.json`
3. 提交前建议做最小校验：
```bash
python3 -m json.tool .claude-plugin/marketplace.json
```
