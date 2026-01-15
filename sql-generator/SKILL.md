---
name: sql-generator
description: SQL 生成工具，支持根据业务描述快速生成查询 SQL。自动解析 PO 类获取真实表名/字段名、推断表关联关系、提供常用查询模板。适用于：(1) 孤立/缺失关联记录查询，(2) 两表数据差异对比，(3) 复杂多表关联查询，(4) 数据一致性检查，(5) 分组聚合统计。当用户需要编写数据库 SQL 查询时使用。在开始编写 SQL 前，必须先确认所有约束条件（表名、字段名、枚举值等）。
---

# SQL Generator

根据业务描述快速生成 SQL 查询语句。

## 工作流程

```
Step 0: 探索与验证表结构
    ↓
Step 1: 收集需求与确认约束（CRITICAL - 必须执行）
    ↓
Step 2: 展示 SQL 计划并确认（CRITICAL - 必须执行）
    ↓
Step 3: 编写 SQL 并落地
    ↓
Step 4: 同步文档
```

## Step 0: 探索与验证表结构

从用户描述中提取表名，然后：
- 搜索 PO 类：`find . -name "*PO.java" -path "*/spi/model/po/*"`
- 读取 `@TableName` 获取真实表名
- 读取 `@TableField` 获取字段映射

**关键：不要猜测表名！** 类名 `GenMatPriceSpecLinkPO` 的实际表名是 `mat_price_spec_link`。

详见 [schema-discovery.md](references/schema-discovery.md)

## Step 1: 收集需求与确认约束（CRITICAL）

**在进入下一步前，必须确认所有约束条件。任何不确定的条件都需使用 AskUserQuestion 工具向用户确认。**

### 确认检查清单

| 检查项 | 说明 | 不确定时的操作 |
|--------|------|----------------|
| 表名 | 用户提到的表名是否为 PO 类对应的真实表名？ | 先搜索 PO 类验证，找不到则询问用户 |
| 字段名 | 用户提到的字段名在 PO 类中是否存在？ | 搜索 PO 类，不存在则询问用户正确的字段名 |
| 枚举值 | 状态/类型字段的值（如 'AWARDED', 'WINNED'）是否正确？ | **必须询问用户确认**，不要自行推测替代方案 |
| 关联关系 | 表之间的关联字段是否明确？ | 检查 PO 类外键，不明确则询问用户 |
| 聚合维度 | 统计查询的分组维度是否清晰？ | 确认 GROUP BY 字段和聚合函数 |

### 典型错误案例（必须避免）

```
错误做法：
用户说：查询 award_status='AWARDED' 的记录
实际：PO 类中没有 award_status 字段
AI 行为：自行改用 response_status='AWARDED'（推测用户意图）
结果：枚举值错误，应该是 award_flag='WINNED'

正确做法：
用户说：查询 award_status='AWARDED' 的记录
AI 行为：
  1. 搜索 PO 类，发现没有 award_status 字段
  2. 使用 AskUserQuestion 询问用户：
     "未找到 award_status 字段。发现可能的字段：award_flag, status
      请确认：(1) 使用哪个字段？(2) 枚举值是什么？"
```

## Step 2: 展示 SQL 计划并确认（CRITICAL）

**在编写 SQL 之前，必须展示计划给用户确认。用户确认后才能开始编写。**

### 计划模板

```markdown
## SQL 生成计划

**查询目标**: [一句话描述查询目的]

**涉及表**:
- `table_a` (表说明) - 关联字段：xxx_id
- `table_b` (表说明) - 关联字段：yyy_id

**过滤条件**:
- field_name = 'value'

**输出字段**:
- field1 AS 别名1
- field2 AS 别名2

**输出文件**: .claude/script/sql-generator/[name].sql

---

**确认生成 SQL？回复 "OK" 或 "Confirm" 继续**
```

### 用户响应处理

| 用户响应 | 操作 |
|----------|------|
| "OK", "Confirm", "确认" | 继续 Step 3 |
| 修改意见 | 根据意见更新计划，再次展示确认 |
| 其他 | 询问用户是否需要调整计划 |

## Step 3: 选择查询模板并生成 SQL

根据需求类型选择模板：

| 需求类型 | 模板 |
|----------|------|
| A表有但B表没有 | orphan-records |
| 对比两表差异 | data-diff |
| 缺失关联检查 | missing-relations |
| 双向关联检查 | bidirectional-check |
| 分组聚合统计 | count-aggregation |

详见 [sql-templates.md](references/sql-templates.md)

### 填充模板参数

将实际表名和字段名替换模板变量：
- `{table_a}` → 主表名
- `{table_b}` → 关联表名
- `{lookup_table}` → 查找表（如 gen_mat_md）
- `{join_key}` → 关联字段

### 验证 SQL

检查：
- [ ] 所有表名都来自 `@TableName`
- [ ] 所有字段名都来自 `@TableField`
- [ ] 已添加 `deleted = 0` 过滤
- [ ] JOIN 条件完整

### 输出结果

将 SQL 写入 `.claude/script/sql-generator/[name].sql`，输出格式：

```markdown
## SQL 查询：[描述]

\`\`\`sql
SELECT ...
\`\`\`

---

## 📊 预览
- 建议先执行 COUNT(*) 预览影响行数
- 添加 LIMIT 10 查看样例数据

## ⚠️ 注意事项
- 已添加 deleted = 0
- 表名来自 PO 类注解

## 📁 文件位置
.claude/script/sql-generator/[name].sql
```

## Step 4: 同步文档

将新发现的表结构和字段信息同步到项目文档。

### 文档目录结构

```
.claude/doc/sql-generator/
├── database-schema.md      # 表结构文档（人工可读）
├── table-registry.json     # 表注册表（机器可读）
└── field-registry.json     # 字段注册表（机器可读）
```

### 1. 更新 database-schema.md

追加表结构到 `.claude/doc/sql-generator/database-schema.md`：

```markdown
## 表名: srm_tsrc_result_header_tr

| 字段名 | 类型 | 说明 | 枚举值 |
|--------|------|------|--------|
| id | bigint | 主键 | - |
| supplier_id | bigint | 供应商ID | - |
| award_flag | varchar(256) | 中标标记 | WINNED, ... |

**关联关系**:
- tsrc_supplier_id → srm_tsrc_supplier_tr.id
```

### 2. 更新 table-registry.json

追加表信息到 `.claude/doc/sql-generator/table-registry.json`：

```json
{
  "tables": [
    {
      "tableName": "srm_tsrc_result_header_tr",
      "poClass": "io.terminus.tsrm.sourcing.spi.model.award.po.SrmTsrcResultHeaderTrPO",
      "description": "寻源结果表",
      "relations": [
        {"field": "supplier_id", "targetTable": "srm_tsrc_supplier_tr", "targetField": "supplier_id"}
      ]
    }
  ]
}
```

### 3. 更新 field-registry.json

追加字段信息到 `.claude/doc/sql-generator/field-registry.json`：

```json
{
  "fields": [
    {
      "tableName": "srm_tsrc_result_header_tr",
      "fieldName": "award_flag",
      "fieldType": "varchar",
      "description": "中标标记",
      "enumValues": ["WINNED"]
    }
  ]
}
```

**注意**：
- 所有文档路径必须是项目目录 `.claude/doc/sql-generator/`
- 不是用户目录 `~/.claude/...`

## 常见模式

**孤立记录查询：**
```
用户："找出 price_mat_spec_tr 有但 mat_price_spec_link 没有的记录"
→ 使用 orphan-records 模板
→ 关联：price_spec_sum_tr_mat_links_id = price_spec_id
```

**数据差异对比：**
```
用户："对比两表，找出互相不存在的记录"
→ 使用 data-diff 模板
→ UNION 两个方向的 NOT EXISTS
```

## 自然语言映射

| 用户描述 | SQL 模式 |
|----------|----------|
| "有A但没B" | NOT EXISTS |
| "在A中但不在B中" | LEFT JOIN ... WHERE B.id IS NULL |
| "去重" | DISTINCT |
| "所有涉及的物料" | SELECT DISTINCT mat FROM ... |

## 重要约束

1. **表名必须来自 PO 类注解** - 禁止猜测或使用类名
2. **必须添加 deleted = 0** - 所有查询都需过滤软删除
3. **优先使用 EXISTS** - 比 JOIN 更高效
4. **不确定则询问** - 枚举值、字段名不确定时必须使用 AskUserQuestion 确认
