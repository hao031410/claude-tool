# SQL Query Templates

本文件包含常见的 SQL 查询模式模板，用于快速生成查询语句。

## 模板变量说明

| 变量 | 说明 |
|------|------|
| `{table_a}` | 主表名 |
| `{table_b}` | 关联表名 |
| `{lookup_table}` | 查找表（如 gen_mat_md） |
| `{output_fields}` | 输出字段列表 |
| `{join_key}` | 关联键字段 |
| `{key_fields}` | 主键字段 |

---

## 模板 1: 孤立记录查询 (orphan-records)

**场景：** 找出 tableA 存在但 tableB 不存在的记录

```sql
SELECT DISTINCT {output_fields}
FROM {table_a} a
INNER JOIN {lookup_table} l ON a.{join_key} = l.id
WHERE a.deleted = 0 AND l.deleted = 0
  AND NOT EXISTS (
    SELECT 1 FROM {table_b} b
    WHERE b.{join_key} = a.{join_key}
      AND b.deleted = 0
  );
```

**适用场景：**
- 单向关联缺失（如 price_mat_spec_tr 存在但 mat_price_spec_link 不存在）
- 数据不一致检查

---

## 模板 2: 数据差异对比 (data-diff)

**场景：** 对比两表数据差异，找出互相不存在的记录

```sql
-- 在 tableA 中但不在 tableB 中
SELECT {key_fields}
FROM {table_a}
WHERE deleted = 0
  AND NOT EXISTS (
    SELECT 1 FROM {table_b}
    WHERE {table_b}.{key_field} = {table_a}.{key_field}
      AND deleted = 0
  )
UNION
-- 在 tableB 中但不在 tableA 中
SELECT {key_fields}
FROM {table_b}
WHERE deleted = 0
  AND NOT EXISTS (
    SELECT 1 FROM {table_a}
    WHERE {table_a}.{key_field} = {table_b}.{key_field}
      AND deleted = 0
  );
```

**适用场景：**
- 数据同步检查
- 缺失记录查找

---

## 模板 3: 缺失关联 (missing-relations)

**场景：** 找出应该关联但未关联的记录（LEFT JOIN + IS NULL）

```sql
SELECT a.*, l.{display_fields}
FROM {table_a} a
LEFT JOIN {relation_table} r ON a.{join_key} = r.{join_key}
INNER JOIN {lookup_table} l ON a.{lookup_key} = l.id
WHERE a.deleted = 0 AND l.deleted = 0 AND r.id IS NULL;
```

**适用场景：**
- 检查外键关联缺失
- 数据完整性验证

---

## 模板 4: 双向关联检查 (bidirectional-check)

**场景：** 检查两个表之间的双向关联是否完整

```sql
-- A→B 存在但 B→A 不存在
SELECT a.id, a.{fields}
FROM {table_a} a
INNER JOIN {relation_ab} rab ON a.id = rab.a_id
WHERE a.deleted = 0
  AND NOT EXISTS (
    SELECT 1 FROM {relation_ba} rba
    WHERE rba.b_id = rab.b_id AND rba.deleted = 0
  );
```

**适用场景：**
- 检查反向关联表同步情况
- 如 price_mat_spec_tr ↔ mat_price_spec_link

---

## 模板 5: 记数统计 (count-aggregation)

**场景：** 统计分组记录数

```sql
SELECT
    {group_by_field},
    COUNT(*) AS cnt
FROM {table}
WHERE deleted = 0
GROUP BY {group_by_field}
HAVING COUNT(*) {condition}  -- 如 > 1, = 0, etc.
ORDER BY cnt DESC;
```

**适用场景：**
- 查找重复记录
- 查找孤立分组（COUNT = 0）

---

## 模板 6: 批量插入 (batch-insert)

**场景：** 带自增 ID 的批量插入

```sql
SET @start_id = 1000;
SET @current_id = @start_id;

INSERT INTO {table} (
    id, {field1}, {field2}, ..., deleted
)
SELECT
    (@current_id := @current_id + 1) AS id,
    t.{field1},
    t.{field2},
    ...,
    0 AS deleted
FROM {source_table} t
WHERE {conditions};

-- 更新自增值
SET @max_id = (SELECT MAX(id) FROM {table});
SET @sql = CONCAT('ALTER TABLE {table} AUTO_INCREMENT = ', @max_id + 1);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
```

---

## 自然语言到 SQL 映射

| 用户描述 | SQL 模式 |
|----------|----------|
| "有A但没B" | NOT EXISTS / LEFT JOIN ... WHERE B.id IS NULL |
| "A和B都有" | INNER JOIN / EXISTS |
| "A或B" | OR / UNION |
| "去重" | DISTINCT / GROUP BY |
| "在A中但不在B中" | NOT EXISTS |
| "所有涉及的用户" | SELECT DISTINCT user_id FROM ... |
| "统计数量" | COUNT(*) / GROUP BY |
