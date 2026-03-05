# 字段类型映射规则

> JSON fieldType 与 Java 类型的映射规则

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