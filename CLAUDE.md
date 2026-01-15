# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Skill 库，包含两个独立技能模块：

- **sql-generator**: SQL 生成工具，根据业务描述快速生成查询 SQL
- **product-design**: 通用新产品开发流程（从需求到产品的完整工作流）

---

## 技能使用

当任务匹配以下场景时，优先调用对应技能：

| 场景 | 调用技能 | 说明 |
|------|----------|------|
| 编写数据库查询 SQL | `sql-generator` | 解析 PO 类获取表名/字段，推断表关联，生成 SQL |
| 新产品开发 | `product-design` (内的 `writing-plans`) | 完整开发流程：需求→设计→开发→测试 |
| UI/UX 设计 | `ui-ux-pro-max` | 50+ 样式、21+ 配色、50+ 字体对 |

---

## sql-generator 核心工作流

```
Step 0: 探索与验证表结构（搜索 PO 类，读取 @TableName/@TableField）
    ↓
Step 1: 收集需求与确认约束（CRITICAL - 使用 AskUserQuestion 确认所有不确定项）
    ↓
Step 2: 展示 SQL 计划并确认（CRITICAL - 用户确认后才能编写）
    ↓
Step 3: 选择模板生成 SQL
    ↓
Step 4: 同步文档（更新 .claude/doc/sql-generator/ 下的注册表）
```

### 关键约束

1. **表名必须来自 PO 类** - 禁止猜测！类名 `GenMatPriceSpecLinkPO` 的实际表名可能是 `mat_price_spec_link`
2. **必须添加 `deleted = 0`** - 所有查询都需过滤软删除
3. **不确定则询问** - 枚举值、字段名不确定时必须使用 `AskUserQuestion` 确认
4. **SQL 输出固定目录** - `.claude/script/sql-generator/[name].sql`

### 表结构发现

```bash
# 搜索 PO 类
find . -name "*PO.java" -path "*/spi/model/po/*"

# 反编译 class（当源码不可用）
javap -cp /path/to/jar io.terminus.erp.md.spi.model.po.GenMatMdPO
```

详见：`sql-generator/references/schema-discovery.md`

### SQL 模板

| 需求类型 | 模板文件 |
|----------|----------|
| A表有但B表没有 | orphan-records |
| 对比两表差异 | data-diff |
| 缺失关联检查 | missing-relations |
| 双向关联检查 | bidirectional-check |
| 分组聚合统计 | count-aggregation |

详见：`sql-generator/references/sql-templates.md`

---

## product-design 核心工作流

```
需求收集 → 产品设计 → UI设计 → 系统设计 → 前端开发 → 后端开发 → 自动化测试
   ↓         ↓         ↓         ↓         ↓         ↓         ↓
 确认      确认      确认+预览  确认                (确认)    (必须全部通过)
```

### 关键约束

1. **UI 设计必须让用户选择生成方式** - 不得擅自调用 API
2. **必须生成 UI 预览文件** - `.claude/output/ui-preview.html`
3. **前端像素级还原预览** - 差异 ≤ 1px
4. **UI-需求比对** - 确认前必须比对，发现差异立即讨论
5. **自动化测试强制执行** - 失败则自动修复，直至全部通过才交付

### 中间产物目录

```
.claude/
├── doc/       # 00-progress.md, 01-requirement.md, 02-product-design.md, ...
├── reference/ # 第三方引用
├── script/    # SQL / Shell 脚本
├── temp/      # 临时文件（随时可删）
└── output/    # ui-preview.html, frontend/, backend/
```

详见：`product-design/product_design.md`

---

## 目录公约

所有 Claude 中间产物固定在**项目级**的 `.claude` 目录：

```
.claude/
├── doc/       # 设计、接口、技术方案
├── reference/ # 第三方引用
├── script/    # SQL / Shell / 测试脚本
├── temp/      # 随时可删
└── output/    # 报告、结果、构建产物
```

**注意**：不要放到用户级 `~/.claude/` 目录（除非明确要求）。
