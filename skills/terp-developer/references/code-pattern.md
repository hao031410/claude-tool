# 代码规范与工具类样例

> 本文档定义 Trantor2 项目的代码规范和推荐工具类用法。

## Java（Trantor2/Spring Boot）

### 集合处理

**推荐使用**：
```java
// Spring CollectionUtils
CollectionUtils.isNotEmpty(list)  // ✅ 正确
CollectionUtils.isEmpty(list)      // ✅ 正确

// ❌ 禁止
list != null && !list.isEmpty()    // 错误
list != null && list.size() > 0    // 错误
```

### 字符串处理

**推荐使用**：
```java
// Hutool StrUtil
StrUtil.isBlank(str)      // 判空白（null/空/全空格）✅
StrUtil.isNotEmpty(str)    // 非空判断 ✅
StrUtil.length(str)        // 安全获取长度（null 安全）✅

// Guava（可选）
com.google.common.base.Strings.isNullOrEmpty(str)
```

### 对象判空

**推荐使用**：
```java
// Hutool
ObjectUtil.isNotNull(obj)  // ✅
ObjectUtil.isNull(obj)      // ✅

// Spring
ObjectUtils.isEmpty(obj)    // ✅
```

### 主键生成

**推荐使用**：
```java
// ✅ 正确：使用 IdGenerator
idGenerator.nextId(POClass.class, po);        // 单个
idGenerator.nextIds(POClass.class, poList);   // 批量

// ❌ 禁止：数据库自增 ID
@TableId(type = IdType.AUTO)
private Long id;
```

### Repository 查询

**推荐使用**：
```java
// ✅ 正确：LambdaQueryWrapper
default List<SettItemTrPO> findByStatus(String status) {
    return selectList(new LambdaQueryWrapper<SettItemTrPO>()
        .eq(SettItemTrPO::getStatus, status));
}

// ❌ 禁止：硬编码字段名
selectList(new QueryWrapper<SettItemTrPO>()
    .eq("status", status))  // 容易出错，难以维护
```

### 批量操作

**推荐使用**：
```java
// 批量插入
repo.insertBatch(poList);          // ✅

// 批量转换
converter.dto2poList(dtoList);     // ✅
```

---

## Python（预留）

待补充...

---

## JavaScript/TypeScript（预留）

待补充...