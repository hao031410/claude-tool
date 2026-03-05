# 影响分析方法论

> 全链路影响分析流程和方法

## 影响分析8个检查点

### 1. PO/DTO 同步检查

**检查方法**：
```java
// 使用 IDE 工具查找 DTO
ide_find_references("SettItemTrDTO")

// 对比字段差异
for (Field field : po.getFields()) {
    if (!dto.hasField(field.getName())) {
        // 标记：DTO 缺少字段
    }
}
```

**影响**: ✏️ 必须修改

### 2. Converter 自定义映射检查

**检查方法**：
```java
// Grep 搜索自定义映射
Grep: "@Mapping|@MappingTarget"
```

**影响**:
- 新增字段 → MapStruct 自动映射，无需修改
- 删除字段 → ⚠️ 需检查是否有自定义映射

### 3. Repository 硬编码字段检查

**检查方法**：
```java
// Grep 搜索硬编码字段名
Grep: "LambdaQueryWrapper.*fieldName|.eq(PO::getFieldName"
```

**影响**: ⚠️ 需确认是否有硬编码使用变更字段

### 4. Service 业务逻辑影响

**检查方法**：
```java
// 使用 IDE 工具查找字段引用
ide_find_references("po.getFieldName()")
ide_find_references("dto.getFieldName()")
```

**影响**: ⚠️ 需检查业务逻辑

### 5. Action 层暴露检查

**检查方法**：
```java
// 检查 Controller 返回值
// 检查 @RequestBody 参数
```

**影响**: ✅ 无影响（通常自动暴露）

### 6. 跨模块依赖检查

**检查方法**：
```java
// 1. 扫描 pom.xml 识别外部依赖
Grep: "<artifactId>erp-*</artifactId>"

// 2. 查找外部引用
ide_find_references(includeLibraries=true)
```

**影响**: ❓ 需评估跨模块影响

### 7. 测试文件检查

**检查方法**：
```java
// Glob 查找测试文件
Glob: "**/*Test.java"

// Grep 搜索字段初始化
Grep: "setFieldName|fieldName ="
```

**影响**: ⚠️ 需补充测试数据

### 8. i18n 国际化检查

**检查方法**：
```java
// Glob 查找 i18n 文件
Glob: "**/i18n/*.properties"

// Grep 搜索字段键
Grep: "sett_item_tr.field_name"
```

**影响**: ⚠️ 需补充 i18n 文本

## 语义冲突检测

### 检查规则

1. **字段类型变更**
   ```java
   String → Integer  // 不兼容
   Integer → Long    // 兼容（向上转型）
   String → Date     // 不兼容
   ```

2. **关联模型变更**
   ```java
   mat_id : 物料(GEN_MD$gen_mat_md) → 商品(GEN_MD$gen_commodity_md)
   // 风险：字段名未变但语义完全改变
   ```

3. **字段注释语义变化**
   ```java
   // 原定义：物料编码
   // 新定义：商品编码
   // 风险：同一字段不同含义
   ```

### 检测到冲突时

```markdown
⚠️ 语义冲突检测：

字段 mat_id 存在语义变更：
原定义：物料编码 → GEN_MD$gen_mat_md
新定义：商品编码 → GEN_MD$gen_commodity_md

🔴 风险：
- 现有代码可能依赖物料数据结构
- 数据库已有数据按物料存储

建议方案：
A) 保留 mat_id，新增 commodity_id
B) 确认语义变更，检查影响并迁移数据

阻塞自动执行，等待确认。
```

## 确认机制

### 生成影响评估报告

```markdown
影响范围评估：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️  必须修改：
   • SettItemTrPO.java（+5 字段）
   • SettItemTrDTO.java（+5 字段）

⚠️  需确认：
   • SettItemTrRepo.java
     - findByCategoryId() 使用了新增字段
   • SettItemTrAppService.java:128
     - convertToDTO() 有自定义映射逻辑

✅  无影响：
   • Action 层未直接暴露字段

❓  跨模块检查：
   • erp-finance 模块引用了 SettItemTrPO

是否继续执行修改？
```

### 等待用户确认后执行

使用 AskUserQuestion 工具等待确认