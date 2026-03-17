# 字段类型映射规则

> JSON fieldType 与 Java 类型的映射规则

## 语义嗅探与强制规则 ⚠️

在执行模型转换（特别是 PO → JSON）时，必须遵守以下强制规则：

### 1. 命名规范强制转换
| 场景 | 命名要求 | 示例 |
|:---|:---|:---|
| **JSON Key** | **必须使用下划线** | `"after_sale_id"`, `"order_line_id"` |
| **Java 字段名** | 必须使用小驼峰 | `afterSaleId`, `orderLineId` |
| **数据库字段名** | 必须使用下划线 | ``@TableField("`after_sale_id`")`` |

### 2. OBJECT 类型自动识别（语义嗅探）
若满足以下任一条件，必须识别为 `OBJECT` 类型，严禁简单识别为 `NUMBER`：
- **后缀匹配**：字段名以 `_id` (JSON) 或 `Id` (Java) 结尾，且不是本模型的主键。
- **业务语义**：字段名包含 `mat`, `org`, `user`, `order`, `tra_par`, `after_sale` 等明显的业务实体关键字。

### 3. relationMeta 补全要求
识别为 `OBJECT` 类型后，必须尝试从以下来源补全 `relationMeta`：
1. **现有知识库**：查询 `dependency-knowledge.json` 中是否有相同或类似字段的关联记录。
2. **代码上下文**：检查是否有 `@TableField` 中的 `relationMeta` 注解或注释说明。
3. **猜想与确认**：基于命名习惯推断关联模型（如 `after_sale_id` → `GEN_MD$after_sale_md`），并在输出时标记为 `⚠️ 需确认`。

---

## fieldType 映射表

| fieldType | Java类型 | MyBatis类型 | 示例 |
|-----------|---------|------------|------|
| TEXT | String | VARCHAR | `@TableField("sett_item_code")` |
| NUMBER | Integer/Long/BigDecimal | DECIMAL/INT | `@TableField(value = "sett_qty", scale = 6)` |
| DATE | Date/LocalDateTime | DATETIME | `@TableField("sett_date")` |
| ENUM | String | VARCHAR | 枚举字段 + @see 引用 |
| BOOL | Boolean | TINYINT(1) | `@TableField("is_sdc_cancel_relv")` |
| OBJECT | 外部模型对象 | BIGINT (外键) | `@TableField("mat_id")` + relationMeta |

## 注解映射规则

### TEXT字段
```java
/**
 * 结算项编码
 */
@ApiModelProperty("结算项编码")
@TableField("`sett_item_code`")
private String settItemCode;
```

### NUMBER字段
```java
/**
 * 结算数量
 */
@ApiModelProperty("结算数量")
@TableField("`sett_qty`")
private BigDecimal settQty;  // 对于精度要求高的用BigDecimal
```

### ENUM字段（强制@see引用）
```java
/**
 * 结算项状态
 * @see SettItemStatusDict  // 枚举字典类
 */
@ApiModelProperty("结算项状态")
@TableField("`sett_item_status`")
private String settItemStatus;
```

### OBJECT字段（关联模型）
```java
/**
 * 物料编码
 */
@ApiModelProperty("物料编码")
@TableField("`mat_id`")
private Long matId;  // 存储外键ID

// JSON字义中包含 relationMeta：
{
  "key": "mat_id",
  "props": {
    "fieldType": "OBJECT",
    "relationMeta": {
      "relationType": "LINK",
      "relationModelAlias": "GEN_MD$gen_mat_md"
    }
  }
}
```

## 数字字段精度规则

```json
{
  "key": "sett_qty",
  "props": {
    "fieldType": "NUMBER",
    "intLength": 20,           // 整数位长度
    "scale": 6,                // 小数位长度
    "numberDisplayType": "digit"  // digit(数字)/currency(货币)
  }
}
```

**Java类型映射规则**：
```java
// 整数类型
if (intLength <= 10 && scale == 0) {
    return Integer;  // INTEGER类型
}

// 长整型
if (intLength > 10 && scale == 0) {
    return Long;     // BIGINT类型
}

// 高精度小数
if (scale > 0) {
    return BigDecimal;  // DECIMAL(intLength, scale)
    // @TableField(value = "sett_qty", scale = 6)
}
```

**numberDisplayType 说明**：
- `digit` - 数字显示（纯数字）
- `currency` - 货币显示（金额字段）

## TEXT 字段规则

```json
{
  "key": "sett_item_code",
  "props": {
    "fieldType": "TEXT",
    "length": 32,              // VARCHAR长度
    "encrypted": false,        // 是否加密
    "unique": false,           // 是否唯一
    "required": false          // 是否必填
  }
}
```

**Java映射**：
```java
@ApiModelProperty("结算项编码")
@TableField("`sett_item_code`")
private String settItemCode;  // length <= 255时为VARCHAR, > 255时为TEXT
```

## ENUM 字段规则

```json
{
  "key": "sett_item_status",
  "props": {
    "fieldType": "ENUM",
    "length": 256,
    "dictPros": {
      "multiSelect": false,    // 是否多选
      "dictValues": [
        {
          "label": "已创建",
          "value": "CREATED"
        },
        {
          "label": "已汇单",
          "value": "SETT_DOC_CREATED"
        }
      ]
    }
  }
}
```

**Java映射**：
```java
/**
 * 结算项状态
 * @see SettItemStatusDict  // 必须用@see引用字典类
 */
@ApiModelProperty("结算项状态")
@TableField("`sett_item_status`")
private String settItemStatus;
```

## BOOL 字段规则

```json
{
  "key": "is_sdc_cancel_relv",
  "props": {
    "fieldType": "BOOL",
    "defaultValue": false,     // 默认值
    "length": 1                // TINYINT(1)
  }
}
```

**Java映射**：
```java
@TableField("`is_sdc_cancel_relv`")
private Boolean isSdcCancelRelv;
```

## OBJECT 字段规则（关联模型）

```json
{
  "key": "mat_id",
  "props": {
    "fieldType": "OBJECT",
    "relationMeta": {
      "relationType": "LINK",
      "currentModelAlias": "ERP_FIN$sett_item_tr",
      "currentModelFieldAlias": "matId",
      "relationModelAlias": "GEN_MD$gen_mat_md",
      "sync": false,
      "linkRelationModel": false,
      "relationModelKey": "GEN_MD$gen_mat_md"
    }
  }
}
```

**Java映射**：
```java
/**
 * 物料编码
 */
@ApiModelProperty("物料编码")
@TableField("`mat_id`")
private Long matId;  // 存储外键ID（BIGINT类型）
```

**重要**：OBJECT类型字段在JSON中包含完整的relationMeta，但在Java PO中存储为外键ID（Long类型）

## 字段长度规则

```json
{
  "key": "sett_item_code",
  "props": {
    "length": 32,  // VARCHAR(32)
    "encrypted": false
  }
}
```

**Java映射**：
- `length` → VARCHAR(length)
- `length > 255` → TEXT