# DDD 分层架构规范和生成规则

## 项目架构概述

terp 项目采用严格的领域驱动设计（DDD）分层架构。生成代码时需遵守各层职责和约定。

### 模块结构

- **{module}-spi**: 存放服务提供者接口（SPI），包括 PO、DTO 和 Converter 等模型与转换定义
- **{module}-infrastructure**: 存放基础设施层实现，包括 Repository

### 层级顺序

生成模型代码时，必须按以下顺序和规范进行：

1. PO (Persistent Object)
2. DTO (Data Transfer Object)
3. Repository 接口
4. Converter (使用 MapStruct)

## 各层生成规则

### 1. PO (Persistent Object)

**位置**: `{module}-spi/src/main/java/io/terminus/tsrm/partner/spi/model/{模块名}/po/`

**继承**: 必须继承 `io.terminus.common.api.model.BaseModel`

**重要规则**: 禁止在 PO 类中重复定义 `BaseModel` 中已存在的字段。这些字段包括：
- `id`
- `createdAt`, `updatedAt`
- `createdBy`, `updatedBy`
- `version`
- `deleted`
- `requestId`
- `originOrgId`

**命名规范**:
- 字段生成严格遵循驼峰原则
- 例如表名为 `grade_rule`，必须生成为 `gradeRule`，而不是 `gradeRuleId`

**注解**:
```java
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("数据库表名")
public class YourPO extends BaseModel {
    @ApiModelProperty("字段说明")
    @TableField("`column_name`")
    private String fieldName;
}
```

**文件头**:
```java
/**
 * (表名)存储模型
 *
 * @author author
 * @since YYYY-MM-DD HH:mm:ss
 */
```

### 2. DTO (Data Transfer Object)

**位置**: `{module}-spi/src/main/java/io/terminus/tsrm/partner/spi/model/{模块名}/dto/`

**继承**: 必须继承 `io.terminus.common.api.model.BaseModel`

**结构**: 纯数据对象（POJO），可以包含其他 DTO 列表以表示关联关系

**注解**:
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class YourDTO extends BaseModel {
    @ApiModelProperty("字段说明")
    private String fieldName;

    // 可以包含关联的 DTO
    private List<OtherDTO> relatedList;
}
```

**文件头**:
```java
/**
 * 表名(表名)传输模型
 *
 * @author author
 * @since YYYY-MM-DD HH:mm:ss
 */
```

### 3. Repository 接口

**位置**: `{module}-infrastructure/src/main/java/io/terminus/tsrm/partner/infrastructure/repo/{模块名}/`

**继承**: 必须继承 `io.terminus.common.mybatis.repository.BaseRepository<对应的PO类>`

**注解**: `@Repository`

**命名**: 必须以 `Repo` 结尾

```java
@Repository
public interface YourRepo extends BaseRepository<YourPO> {
}
```

**文件头**:
```java
/**
 * 表名(表名)表数据库访问层
 *
 * @author author
 * @since YYYY-MM-DD HH:mm:ss
 */
```

### 4. Converter (MapStruct)

**位置**: `{module}-spi/src/main/java/io/terminus/tsrm/partner/spi/convert/{模块名}/`

**实现**: 使用 MapStruct 框架

**注解**:
```java
@Mapper(componentModel = "spring")
```

**处理嵌套对象**:
如果 DTO 包含其他 DTO 列表，使用 `uses = {被引用的Converter.class}` 来注入子转换器

**标准方法签名**:
```java
YourDTO po2Dto(YourPO po);
List<YourDTO> po2DtoList(List<YourPO> poList);
YourPO dto2Po(YourDTO dto);
List<YourPO> dto2PoList(List<YourDTO> dtoList);
```

**文件头**:
```java
/**
 * 表名(表名)结构映射器
 *
 * @author author
 * @since YYYY-MM-DD HH:mm:ss
 */
```

## 输入 JSON 格式

用户提供的 JSON 应包含以下信息：

```json
{
  "tableName": "grade_rule",
  "moduleName": "grade",
  "projectName": "terp-partner",
  "fields": [
    {
      "name": "grade_name",
      "type": "String",
      "comment": "等级名称"
    },
    {
      "name": "grade_score",
      "type": "Integer",
      "comment": "等级分数"
    },
    {
      "name": "grade_discount",
      "type": "BigDecimal",
      "comment": "等级折扣"
    }
  ]
}
```

### 字段类型映射

| 数据库类型 | Java 类型 |
|-----------|-----------|
| VARCHAR, TEXT, CHAR | String |
| INT, TINYINT, SMALLINT | Integer |
| BIGINT | Long |
| DECIMAL, NUMERIC | BigDecimal |
| DATETIME, TIMESTAMP | LocalDateTime |
| DATE | LocalDate |
| BOOLEAN, TINYINT(1) | Boolean |
| DOUBLE | Double |
| FLOAT | Float |

## 生成流程

1. **询问基本信息**:
   - 项目名称（如 `terp-partner`）
   - 模块名称（如 `grade`）
   - 获取用户提供的 JSON

2. **解析 JSON**:
   - 提取表名、模块名、字段列表
   - 驼峰转换表名和字段名

3. **按顺序生成**:
   - 生成 PO
   - 生成 DTO
   - 生成 Repository
   - 生成 Converter

4. **确认生成位置**:
   - 在生成前，向用户展示将要生成的文件路径
   - 获得确认后再生成

## 命名转换规则

### 表名到类名
- `grade_rule` → `GradeRule`
- `order_header` → `OrderHeader`
- `user_info` → `UserInfo`

### 字段名转换
- `grade_name` → `gradeName`
- `order_status` → `orderStatus`

### 文件路径
- PO: `{module}-spi/src/main/java/io/terminus/tsrm/partner/spi/model/{module}/po/{EntityName}PO.java`
- DTO: `{module}-spi/src/main/java/io/terminus/tsrm/partner/spi/model/{module}/dto/{EntityName}DTO.java`
- Repo: `{module}-infrastructure/src/main/java/io/terminus/tsrm/partner/infrastructure/repo/{module}/{EntityName}Repo.java`
- Converter: `{module}-spi/src/main/java/io/terminus/tsrm/partner/spi/convert/{module}/{EntityName}Converter.java`

## 包路径规范

所有代码的基包路径为：
```java
// SPI 模块
io.terminus.tsrm.partner.spi

// Infrastructure 模块
io.terminus.tsrm.partner.infrastructure
```

注意事项：
- 项目名 `terp-partner` 转换为包名时，去掉横杠，首字母小写：`partner`
- 其他 terp 项目（如 `terp-common`）遵循相同规则