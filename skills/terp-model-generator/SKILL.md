---
name: terp-model-generator
description: This skill should be used when the user provides a field array and asks to "generate PO", "generate {EntityName}PO", or mentions generating entity class code from field definitions.
version: 0.1.0
---

# The Terp Model Generator

Transform JSON table definitions into DDD-compliant model layer code (PO, DTO, Repository, Converter) for terp projects.

## When to Use

Use when user:
- Provides JSON and asks to generate corresponding model code
- Requests PO/DTO/Repository/Converter generation for terp projects
- Mentions terp model generation or table-to-model conversion

## Generation Workflow

### 0. Explore Project Package Structure

**CRITICAL**: Before any code generation, MUST explore the project to understand package structure.

**Auto-detection steps**:

1. **Find SPI modules**:
   - Search for directories matching `*-spi/`
   - Example: `tsrm-onlinemall-spi/`, `mall-spi/`

2. **Determine business domain** from base package:
   - Read one PO file to see package structure
   - Extract business domain from package (e.g., `onlinemall`, `mall`)
   - Pattern: `io.terminus.tsrm.{domain}.spi`

3. **List existing modules** using tree command:
   ```bash
   tree -L 3 -d {project}-spi/src/main/java/io/terminus/tsrm/{domain}/spi/model/
   ```
   - Extract module names from tree output
   - Examples: `item`, `mall`, `article`, `basic`, `trade`, `retail`, `commodity`, `mat`, `reuse`

4. **If tree command fails**:
   - Fall back to: `find {project}-spi/src/main/java/io/terminus/tsrm/{domain}/spi/model -type d -maxdepth 2`
   - Remind user: "tree command not found, using find instead. Install tree for better visualization."

5. **Report findings to user**:
   ```
   Found SPI module: tsrm-onlinemall-spi
   Base package: io.terminus.tsrm.onlinemall.spi
   Available modules: item, mall, article, basic, trade, retail, commodity, mat, reuse
   ```

6. **Ask user to confirm or specify**:
   - Which module to use for the new entity?
   - Or use user-provided package path if already given

**Package structure template**:
```
{project}-spi/src/main/java/io/terminus/tsrm/{domain}/spi/
├── model/
│   └── {module}/
│       ├── po/           ← PO classes
│       ├── dto/          ← DTO classes
│       ├── req/          ← Request classes
│       ├── so/           ← Search Object classes
│       └── vo/           ← View Object classes
├── dict/
│   └── {module}/         ← Dictionary/Enum interfaces
└── convert/
    └── {module}/         ← MapStruct converters

{project}-infrastructure/src/main/java/io/terminus/tsrm/{domain}/infrastructure/repo/{module}/
                        ← Repository interfaces
```

### 1. Gather Required Information

Ask for:
- Target entity name and package to generate (e.g., `io.terminus.tsrm.mall.spi.model.mall.po.ProductInfoMdPO`)
- JSON response from Trantor/Low-Code platform

**JSON Response Format**:

User provides a response object with this structure:
```json
{
  "requestId": "...",
  "success": true,
  "data": [
    {
      "key": "MALL$product_info_md",
      "name": "产品信息",
      "props": {
        "tableName": "product_info_md"
      },
      "children": [
        {
          "key": "product_code",
          "name": "产品编码",
          "alias": "productCode",
          "props": {
            "fieldType": "TEXT",
            "comment": "产品编码。",
            "columnName": "product_code"
          }
        }
      ]
    }
  ]
}
```

**Extract fields from**: `data[0].children`

### 2. Parse Target Entity

Extract from target entity path:
- Package: e.g., `io.terminus.tsrm.mall.spi.model.mall.po`
- Class name: e.g., `ProductInfoMdPO`
- Entity name (without PO): e.g., `ProductInfoMd`
- Module name from package: e.g., `mall`

**Determine table name**:
- Priority 1: From JSON `data[0].props.tableName`
- Priority 2: Convert class name to Pascal to snake: `ProductInfoMdPO` → `product_info_md`

### 3. Parse Field Properties

**Extract fields from**: `data[0].children`

**IMPORTANT**: Filter out system fields where `props.isSystemField == true`
These include: `id`, `created_by`, `updated_by`, `created_at`, `updated_at`, `version`, `deleted`, `request_id`, `origin_org_id`, `tenant_id`

**DO NOT generate** these fields in PO as they are already in BaseModel.

**SPECIAL HANDLING for PARENT_CHILD relationships**:
- If `fieldType: "OBJECT"` AND `relationType: "PARENT_CHILD"`:
  - **DO NOT generate** this field in PO (represents one-to-many relationship)
  - **GENERATE** `List<RelatedEntityDTO>` field in DTO (not List<RelatedDTO>)
  - Example: If field `items` references `OrderItemPO`, DTO field should be `List<OrderItemDTO> items`

From each non-system field object in the array:
- **Field name**: `alias` (use camelCase directly: `productCode`)
- **Column name**: `props.columnName` (use snake_case with backticks)
- **Comment**: `props.comment`
- **Java type**: Map `props.fieldType` to Java types
- **Type handler**: For ATTACHMENT fields, add JacksonTypeHandler

**Field Type Mapping**:

| fieldType | Java Type | Notes |
|-----------|-----------|-------|
| TEXT | String | Basic text fields |
| ENUM | String | Enum type (add @see annotation to Dict class) |
| NUMBER | BigDecimal | Use BigDecimal for all numeric fields |
| OBJECT | Long | Store as Long (reference ID) in PO |
| DATE | java.time.LocalDateTime | Date/time (trantor uses DATE for timestamp) |
| DATETIME | java.time.LocalDateTime | Date time |
| ATTACHMENT | String (single) or List<String> (multi) | Attachment, check `multi` property |
| BOOLEAN | Boolean | Boolean type |

**Type Handlers**:
- If `fieldType: "ATTACHMENT"` AND `multi === true`:
  - Type: `List<String>`
  - Add `@TableField(typeHandler = JacksonTypeHandler.class)`
- If `fieldType: "ATTACHMENT"` AND `multi === false`:
  - Type: `String` (single attachment/image)
  - No type handler needed
- If `fieldType: "OBJECT"` → Store as Long (ID reference) in PO

**Enum Fields Special Handling**:

**Detect ENUM fields**: Field has `fieldType: "ENUM"` and `props.dictPros` exists (contains dictValues array)

**Generate three artifacts for each ENUM field**:

1. **Add import statement in PO**:
```java
import io.terminus.tsrm.{domain}.spi.dict.{module}.{EntityName}{PascalCaseFieldName}Dict;
```

2. **Add @see annotation in PO** (using simple class name):
```java
/**
 * @see {EntityName}{PascalCaseFieldName}Dict
 */
@ApiModelProperty("{comment}")
@TableField("`{column_name}`")
private String {camelCaseFieldName};
```

3. **Add import and @see annotation in DTO** (same as PO):

3. **Generate Dict interface class**:

**Location**: `{module}-spi/src/main/java/io/terminus/tsrm/{package}/spi/dict/{module}/{EntityName}{PascalCaseFieldName}Dict.java`

**Template**:
```java
package io.terminus.tsrm.{package}.spi.dict.{module};

/**
 * {field_name}({EntityName}{PascalCaseFieldName})字典
 *
 * @author claude
 * @since  {timestamp}
 */
public interface {EntityName}{PascalCaseFieldName}Dict {

    /**
     * {label}
     */
    String {CONSTANT_VALUE} = "{value}";

}
```

**Dict class naming**:
- Pattern: `{EntityName}{PascalCaseFieldName}Dict`
- Example: `SrmMalItemMd` + `item_type` → `SrmMalItemMdItemTypeDict`

**Constant naming**:
- Convert `value` to uppercase
- Example: `electronic` → `ELECTRONIC`

**Example input**:
```json
[{
  "key": "report_format",
  "name": "报告形式",
  "props": {
    "fieldType": "ENUM",
    "comment": "报告形式。",
    "columnName": "report_format",
    "dictPros": {
      "dictValues": [
        {"label": "电子版", "value": "electronic"},
        {"label": "纸质版", "value": "paper"}
      ]
    }
  }
}]
```

**Generated PO field** (with import):
```java
import io.terminus.tsrm.onlinemall.spi.dict.item.TestReportReportFormatDict;

// ...

/**
 * @see TestReportReportFormatDict
 */
@ApiModelProperty("报告形式。")
@TableField("`report_format`")
private String reportFormat;
```

**Generated DTO field** (with import):
```java
import io.terminus.tsrm.onlinemall.spi.dict.item.TestReportReportFormatDict;

// ...

/**
 * @see TestReportReportFormatDict
 */
@ApiModelProperty("报告形式。")
private String reportFormat;
```

**Generated Dict class**:
```java
package io.terminus.tsrm.onlinemall.spi.dict.item;

/**
 * 报告形式(TestReportReportFormat)字典
 *
 * @author system
 * @since 2025-01-06 16:40:00
 */
public interface TestReportReportFormatDict {

    /**
     * 电子版
     */
    String ELECTRONIC = "electronic";

    /**
     * 纸质版
     */
    String PAPER = "paper";

}
```

### 3. Generate Files in Order

**Generation order**: PO → Dict classes (for ENUMs) → DTO → Repository → Converter

#### Step 3.1: Generate PO

**Location**: `{module}-spi/src/main/java/io/terminus/tsrm/{package}/spi/model/{module}/po/{EntityName}PO.java`

**Template Pattern**:
```java
package io.terminus.tsrm.{package}.spi.model.{module}.po;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import io.swagger.annotations.ApiModelProperty;
import io.terminus.common.api.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

// Import statements for ENUM Dict classes (one per ENUM field)
// import io.terminus.tsrm.{package}.spi.dict.{module}.{EntityName}{PascalCaseFieldName}Dict;

/**
 * ({table_name})存储模型
 *
 * @author claude
 * @since {timestamp}
 */
@EqualsAndHashCode(callSuper = true)
@Data
@TableName("{table_name}")
public class {EntityName}PO extends BaseModel {
    private static final long serialVersionUID = 1L;

    // For TEXT/ENUM fields
    @ApiModelProperty("{comment}")
    @TableField("`{column_name}`")
    private String textField;

    // For ENUM fields with Dict (import module's Dict package)
    /**
     * @see {EntityName}{EnumFieldName}Dict
     */
    @ApiModelProperty("{comment}")
    @TableField("`{column_name}`")
    private String enumField;

    // For OBJECT fields
    @ApiModelProperty("{comment}")
    @TableField("`{column_name}`")
    private Long objectField;

    // For NUMBER fields
    @ApiModelProperty("{comment}")
    @TableField("`{column_name}`")
    private java.math.BigDecimal numberField;

    // For ATTACHMENT fields (multi: true)
    @ApiModelProperty("{comment}")
    @TableField(value = "`{column_name}`", typeHandler = JacksonTypeHandler.class)
    private List<String> attachmentFieldList;

    // For ATTACHMENT fields (multi: false - single attachment)
    @ApiModelProperty("{comment}")
    @TableField("`{column_name}`")
    private String attachmentField;
}
```

**Critical Rules**:
- Inherit `io.terminus.common.api.model.BaseModel`
- Do NOT define BaseModel fields: `id`, `createdAt`, `updatedAt`, `createdBy`, `updatedBy`, `version`, `deleted`, `requestId`, `originOrgId`, `tenant_id`
- Use strict camelCase for field names from `alias` (e.g., `productCode`)
- Add `@TableField` with backticks for column names
- For ENUM fields, add explicit `import` statement for the Dict class AND use simple class name in `@see` comment
- For ATTACHMENT fields:
  - If `multi === true`: use `List<String>` type with JacksonTypeHandler
  - If `multi === false`: use `String` type without type handler
- **Field order**: Do NOT need to maintain any specific field order - can generate in any convenient order

#### Step 3.2: Generate Dict Classes (only for ENUM fields)

**Skip this step** if no fields have `fieldType: "ENUM"`.

**For each ENUM field**:

1. Generate Dict interface at:
   `{module}-spi/src/main/java/io/terminus/tsrm/{package}/spi/dict/{module}/{EntityName}{PascalCaseFieldName}Dict.java`

2. Use template from "Enum Fields Special Handling" section

3. For each `dictValue` in `props.dictPros.dictValues`:
   - Create constant: `String {UPPERCASE_VALUE} = "{value}";`
   - Add JavaDoc: `/** {label} */`

#### Step 3.3: Generate DTO

**Location**: `{module}-spi/src/main/java/io/terminus/tsrm/{package}/spi/model/{module}/dto/{EntityName}DTO.java`

**Template Pattern**:
```java
package io.terminus.tsrm.{package}.spi.model.{module}.dto;

import io.swagger.annotations.ApiModelProperty;
import io.terminus.common.api.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

// Import statements for ENUM Dict classes (one per ENUM field)
// import io.terminus.tsrm.{package}.spi.dict.{module}.{EntityName}{PascalCaseFieldName}Dict;

/**
 * {table_name}({table_name})传输模型
 *
 * @author claude
 * @since {timestamp}
 */
@EqualsAndHashCode(callSuper = true)
@Data
public class {EntityName}DTO extends BaseModel {
    private static final long serialVersionUID = 1L;

    /**
     * @see {EntityName}{EnumFieldName}Dict
     */
    @ApiModelProperty("{comment}")
    private String enumField;

    // Include related DTO objects or lists for relationships
    private OtherDTO relatedObject;
    private List<OtherDTO> relatedList;
}
```

**Rules**:
- Inherit `io.terminus.common.api.model.BaseModel`
- Pure data object (POJO)
- Can include other DTO objects or lists for relationships
- For ENUM fields, add explicit `import` statement for the Dict class AND use simple class name in `@see` comment
- **For PARENT_CHILD relationships** (fieldType: "OBJECT" + relationType: "PARENT_CHILD"):
  - Generate field as `List<RelatedEntityDTO>` type
  - Example: field `items` referencing `OrderItemPO` → `private List<OrderItemDTO> items;`

#### Step 3.4: Generate Repository

**Location**: `{module}-infrastructure/src/main/java/io/terminus/tsrm/{package}/infrastructure/repo/{module}/{EntityName}Repo.java`

**Template Pattern**:
```java
package io.terminus.tsrm.{package}.infrastructure.repo.{module};

import io.terminus.common.mybatis.repository.BaseRepository;
import io.terminus.tsrm.{package}.spi.model.{module}.po.{EntityName}PO;
import org.springframework.stereotype.Repository;

/**
 * {table_name}({table_name})表数据库访问层
 *
 * @author claude
 * @since {timestamp}
 */
@Repository
public interface {EntityName}Repo extends BaseRepository<{EntityName}PO> {
}
```

**Rules**:
- Inherit `io.terminus.common.mybatis.repository.BaseRepository<{EntityName}PO>`
- Must have `@Repository` annotation
- Name must end with `Repo`

#### Step 3.5: Generate Converter

**Location**: `{module}-spi/src/main/java/io/terminus/tsrm/{package}/spi/convert/{module}/{EntityName}Converter.java`

**Template Pattern**:
```java
package io.terminus.tsrm.{package}.spi.convert.{module};

import io.terminus.tsrm.{package}.spi.model.{module}.po.{EntityName}PO;
import io.terminus.tsrm.{package}.spi.model.{module}.dto.{EntityName}DTO;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

/**
 * {table_name}({table_name})结构映射器
 *
 * @author claude
 * @since {timestamp}
 */
@Mapper(componentModel = "spring", unmappedTargetPolicy = org.mapstruct.ReportingPolicy.IGNORE)
public interface {EntityName}Converter {

    @Mapping(target = "nestedObject.id", source = "nestedObject")
    @Mapping(target = "otherObject.id", source = "otherObject")
    {EntityName}DTO po2Dto({EntityName}PO req);

    @Mapping(target = "nestedObject", source = "nestedObject.id")
    @Mapping(target = "otherObject", source = "otherObject.id")
    {EntityName}PO dto2Po({EntityName}DTO req);

    List<{EntityName}DTO> po2DtoList(List<{EntityName}PO> poList);

    List<{EntityName}PO> dto2PoList(List<{EntityName}DTO> dtoList);
}
```

**Rules**:
- Use MapStruct framework with `unmappedTargetPolicy = org.mapstruct.ReportingPolicy.IGNORE`
- Add `@Mapping` import for nested object mappings
- Method parameter name should be `req` (not `po`/`dto`)
- For OBJECT fields in PO (Long references), add `@Mapping`:
  - `po2Dto`: `@Mapping(target = "nestedObject.id", source = "nestedObject")`
  - `dto2Po`: `@Mapping(target = "nestedObject", source = "nestedObject.id")`
- List conversion methods (`po2DtoList`, `dto2PoList`) do NOT need `@Mapping` annotations

### 4. Before Generation Confirmation

After parsing JSON, present to user:

**Generated File Locations**:
- PO: `{project}-spi/src/main/java/io/terminus/tsrm/{package}/spi/model/{module}/po/{EntityName}PO.java`
- Dict classes (if any ENUM fields): `{project}-spi/src/main/java/io/terminus/tsrm/{package}/spi/dict/{module}/{EntityName}{PascalCaseFieldName}Dict.java`
- DTO: `{project}-spi/src/main/java/io/terminus/tsrm/{package}/spi/model/{module}/dto/{EntityName}DTO.java`
- Repo: `{project}-infrastructure/src/main/java/io/terminus/tsrm/{package}/infrastructure/repo/{module}/{EntityName}Repo.java`
- Converter: `{project}-spi/src/main/java/io/terminus/tsrm/{package}/spi/convert/{module}/{EntityName}Converter.java`

**Summary**:
- Entity: {EntityName}
- Table: {table_name}
- Module: {module}
- Total fields: {count} fields
- ENUM fields: {enum_count} (will generate {enum_count} Dict classes)

Ask user to confirm before generating.

### 5. Naming Conversion Rules

#### Table Name to Class Name
- Snake case to Pascal case
- `grade_rule` → `GradeRule`
- `order_header` → `OrderHeader`

#### Field Name to Java Field
- Snake case to camel case
- `grade_name` → `gradeName`
- `order_status` → `orderStatus`

#### Project Name to Package Name
- Remove hyphen, lowercase
- `terp-partner` → `partner`
- `terp-onlinemall` → `onlinemall`

## Type Mapping

| Database Type | Java Type |
|---------------|-----------|
| VARCHAR, TEXT, CHAR | String |
| INT, TINYINT, SMALLINT | Integer |
| BIGINT | Long |
| DECIMAL, NUMERIC | BigDecimal |
| DATETIME, TIMESTAMP | java.time.LocalDateTime |
| DATE | java.time.LocalDate |
| BOOLEAN, TINYINT(1) | Boolean |
| DOUBLE | Double |
| FLOAT | Float |

## File Organization

**Base Package Paths**:
```java
// SPI module
io.terminus.tsrm.{package}.spi

// Infrastructure module
io.terminus.tsrm.{package}.infrastructure
```

**Directory Structure**:
```
{project}-spi/src/main/java/io/terminus/tsrm/{package}/spi/
  ├── model/
  │   └── {module}/
  │       ├── po/
  │       └── dto/
  └── convert/
      └── {module}/

{project}-infrastructure/src/main/java/io/terminus/tsrm/{package}/infrastructure/
  └── repo/
      └── {module}/
```

## Additional Resources

### Working Examples

Consult working examples in `examples/`:
- **`GradeRulePO.java`** - Simple PO example
- **`GradeRuleDTO.java`** - Simple DTO example
- **`GradeRuleRepo.java`** - Simple Repository example
- **`GradeRuleConverter.java`** - MapStruct Converter example

### Reference Documentation

For detailed DDD architecture specifications:
- **`references/ddd-architecture-spec.md`** - Complete DDD layer rules and generation guidelines

## Common Mistakes to Avoid

### 1. Duplicating BaseModel Fields

❌ Do NOT define these fields in PO:
```java
private Long id;           // Already in BaseModel
private LocalDateTime createdAt;  // Already in BaseModel
private String createdBy;   // Already in BaseModel
```

### 2. Incorrect Naming

❌ Bad field naming:
- `gradeRuleId` (should be `gradeRule` when table is `grade_rule`)

✅ Correct naming:
- `grade_rule` → `gradeRule`

### 3. Missing Annotations

❌ Missing required annotations:
```java
@TableName("grade_rule")  // Required
@TableField("`grade_name`")  // Required for column mapping
```

### 4. Wrong Generation Order

Always generate in this order:
1. PO (Persistent Object)
2. DTO (Data Transfer Object)
3. Repository (Interface)
4. Converter (MapStruct)

### 5. Incorrect Type Mapping

❌ Wrong mapping:
- `DECIMAL` → `Double` (should be `BigDecimal`)

✅ Correct mapping:
- `DECIMAL` → `BigDecimal`

## Package Conversion Examples

| Project Name | Package Name |
|-------------|--------------|
| terp-partner | partner |
| terp-onlinemall | onlinemall |
| terp-common | common |
| terp-price | price |
| tsrm-partner | partner |

Replace `terp` with `tsrm` when appropriate - project names may use either prefix.