# 表结构发现指南

本文件说明如何从 Java PO 类发现真实的数据库表名和字段映射。

## 核心原则

**不要猜测表名和字段名！** 必须从 PO 类的注解中获取真实值。

## 发现流程

### 1. 定位 PO 类

PO 类通常位于：
- `*spi*/src/main/java/io/terminus/*/spi/model/base/po/`
- 文件名模式：`*PO.java`

搜索命令：
```bash
find . -name "*PO.java" -path "*/spi/model/po/*"
```

### 2. 解析表名 (@TableName)

使用 `@TableName` 注解获取真实表名：

```java
@TableName(value = "price_mat_spec_tr")
public class PriceMatSpecTrPO extends BaseModel {
    ...
}
```

**注意：** 类名可能不等于表名！
- 类名：`GenMatPriceSpecLinkPO`
- 表名：`mat_price_spec_link`

### 3. 解析字段映射 (@TableField)

使用 `@TableField` 注解获取真实字段名：

```java
@TableField("`mat`")
private Long mat;

@TableField("`price_spec_sum_tr_mat_links_id`")
private Long priceSpecSumTrMatLinksId;
```

**注意：** Java 字段名（驼峰）≠ 数据库字段名（下划线）

### 4. 反编译 Class 文件

当源码不可用时，使用 javap 反编译：

```bash
# 从 jar 包反编译
javap -cp /path/to/jar io.terminus.erp.md.spi.model.po.mat.GenMatMdPO

# 从编译输出反编译
javap -cp ./target/classes io.terminus.tsrm.price.lib.spi.model.base.po.PriceMatSpecTrPO
```

### 5. 公共字段 (BaseModel)

所有 PO 类继承自 `BaseModel`，包含以下公共字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Long | 主键 |
| createdAt | DateTime | 创建时间 |
| updatedAt | DateTime | 更新时间 |
| createdBy | Long | 创建人 |
| updatedBy | Long | 更新人 |
| deleted | Long/Boolean | 软删除（0=未删除） |

**重要：** 查询时必须添加 `deleted = 0`

## 表结构缓存

发现的表结构应缓存到 `.claude/doc/table-registry.json`：

```json
{
  "tables": {
    "price_mat_spec_tr": {
      "poClass": "PriceMatSpecTrPO",
      "module": "tsrm-price-lib-spi",
      "fields": {
        "id": "Long",
        "mat": "Long",
        "mat_name": "String",
        "price_spec_sum_tr_mat_links_id": "Long",
        "mat_spec": "String"
      },
      "relations": {
        "gen_mat_md": {"type": "many-to-one", "join": "mat = id"},
        "price_spec_sum_tr": {"type": "many-to-one", "join": "price_spec_sum_tr_mat_links_id = id"}
      }
    }
  }
}
```

## 关联关系推断

### 外键识别模式

| 字段名模式 | 关联目标 |
|-----------|---------|
| `xxx_id` | 通常关联到 `xxx.id` |
| `mat` | 关联到 `gen_mat_md.id` |
| `brand_id` | 关联到 `brand` 表的 id |

### 双向关联识别

如果 tableA 有字段 `xxx_id`，tableB 有字段 `yyy_id`，且：
- `tableA.xxx_id = tableB.id`
- `tableB.yyy_id = tableA.id`

则可能是双向关联。

## 常见表名映射

| 类名 | 表名 |
|------|------|
| GenMatMdPO | gen_mat_md |
| GenMatPriceSpecLinkPO | mat_price_spec_link |
| PriceMatSpecTrPO | price_mat_spec_tr |
| PriceSpecSumTrPO | price_spec_sum_tr |
| PriceTransferTrPO | price_transfer_tr |
