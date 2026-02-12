# Java 包结构自动探测指南

## 探测目标

在生成代码前，skill 必须自动探测项目的包结构，确定：
1. SPI 模块目录名称（如 `tsrm-onlinemall-spi`）
2. 业务域名称（business domain，如 `onlinemall`）
3. 可用的模块列表（modules，如 `item`, `mall`, `article` 等）

## 探测步骤

### 步骤 1: 查找 SPI 模块

使用 Glob 查找所有符合 `*-spi` 模式的目录：

```bash
Glob: **/*-spi/
```

可能的示例：
- `tsrm-onlinemall-spi/`
- `mall-spi/`
- `tsrm-partner-spi/`

**如果找到多个 SPI 模块**，询问用户选择哪一个。

### 步骤 2: 确定业务域

读取任意一个 PO 文件，提取包名：

```java
// 示例包名：
package io.terminus.tsrm.onlinemall.spi.model.item.po;
```

从中提取 business domain：`onlinemall`

包名模式：
```
io.terminus.tsrm.{business-domain}.spi.model.{module}.po
```

### 步骤 3: 列出所有可用模块

使用 Glob 查找所有 PO 目录：

```bash
Glob: **/spi/model/*/po/*.java
```

从路径中提取模块名称：

```
spi/model/item/po/*.java      → module: item
spi/model/mall/po/*.java      → module: mall
spi/model/article/po/*.java   → module: article
spi/model/basic/po/*.java     → module: basic
spi/model/trade/po/*.java     → module: trade
spi/model/retail/po/*.java    → module: retail
spi/model/commodity/po/*.java → module: commodity
spi/model/mat/po/*.java       → module: mat
spi/model/reuse/po/*.java     → module: reuse
```

### 步骤 4: 向用户报告并确认

```text
发现 SPI 模块：tsrm-onlinemall-spi
基础包：io.terminus.tsrm.onlinemall.spi

可用模块：
- item: 商品相关
- mall: 商城相关
- article: 文章相关
- basic: 基础配置
- trade: 交易相关
- retail: 零售相关
- commodity: 商品中心
- mat: 物料管理
- reuse: 利旧管理

请选择要添加新实体的模块，或直接提供完整包路径。
```

## 完整包结构模板

### SPI 模块

```
{project}-spi/src/main/java/io/terminus/tsrm/{business-domain}/spi/
├── model/
│   └── {module}/
│       ├── po/           ← PO 持久对象
│       ├── dto/          ← DTO 传输对象
│       ├── req/          ← Request 请求对象
│       ├── so/           ← Search Object 搜索对象
│       └── vo/           ← View Object 视图对象
├── dict/
│   └── {module}/         ← 字典/枚举接口
└── convert/
    └── {module}/         ← MapStruct 转换器
```

### Infrastructure 模块

```
{project}-infrastructure/src/main/java/io/terminus/tsrm/{business-domain}/infrastructure/
└── repo/
    └── {module}/         ← Repository 接口
```

## 文件路径映射

给定实体类名：`SrmMalItemMdPO`

| 组件 | 文件路径 |
|------|---------|
| PO | `{project}-spi/src/main/java/io/terminus/tsrm/{domain}/spi/model/{module}/po/SrmMalItemMdPO.java` |
| DTO | `{project}-spi/src/main/java/io/terminus/tsrm/{domain}/spi/model/{module}/dto/SrmMalItemMdDTO.java` |
| Dict | `{project}-spi/src/main/java/io/terminus/tsrm/{domain}/spi/dict/{module}/SrmMalItemMdItemTypeDict.java` |
| Repo | `{project}-infrastructure/src/main/java/io/terminus/tsrm/{domain}/infrastructure/repo/{module}/SrmMalItemMdRepo.java` |
| Converter | `{project}-spi/src/main/java/io/terminus/tsrm/{domain}/spi/convert/{module}/SrmMalItemMdConverter.java` |

## 实际项目示例

### 示例 1: tsrm-onlinemall 项目

```
tsrm-onlinemall-spi/
└── src/main/java/io/terminus/tsrm/onlinemall/spi/
    ├── model/
    │   ├── item/
    │   │   └── po/
    │   │       └── SrmMalItemMdPO.java
    │   ├── mall/
    │   │   └── po/
    │   │       └── MallProductPO.java
    │   └── trade/
    │       └── po/
    │           └── MalTradeOrderHeadTrPO.java
    ├── dict/
    │   ├── item/
    │   │   └── SrmMalItemMdItemTypeDict.java
    │   └── trade/
    │       └── MalTradeOrderHeadTrStatusDict.java
    └── convert/
        └── item/
            └── SrmMalItemMdConverter.java

tsrm-onlinemall-infrastructure/
└── src/main/java/io/terminus/tsrm/onlinemall/infrastructure/
    └── repo/
        ├── item/
        │   └── SrmMalItemMdRepo.java
        └── trade/
            └── MalTradeOrderHeadTrRepo.java
```

### 示例 2: mall 项目（假设）

```
mall-spi/
└── src/main/java/io/terminus/tsrm/mall/spi/
    └── model/
        └── product/
            └── po/
                └── ProductInfoPO.java

mall-infrastructure/
└── src/main/java/io/terminus/tsrm/mall/infrastructure/
    └── repo/
        └── product/
            └── ProductInfoRepo.java
```

## 自动探测实现要点

### 使用 Glob 模式查找示例

```python
# 查找所有 SPI 模块
glob_pattern: "*-spi/"

# 查找所有 PO 文件以确定模块
glob_pattern: "**/spi/model/*/po/*.java"

# 查找所有 DTO 文件
glob_pattern: "**/spi/model/*/dto/*.java"

# 查找所有 Repo 文件以确定 infrastructure 结构
glob_pattern: "**/infrastructure/repo/*/*Repo.java"
```

### 路径解析示例

给定文件路径：
```
tsrm-onlinemall-spi/src/main/java/io/terminus/tsrm/onlinemall/spi/model/item/po/SrmMalItemMdPO.java
```

解析为：
- Project: `tsrm-onlinemall-spi`
- Domain: `onlinemall` (package 中的业务部分)
- Module: `item` (model 下的模块名)
- Type: `po`
- Class: `SrmMalItemMdPO`

## 常见模块名称

| 模块名 | 业务含义 | 典型实体示例 |
|--------|---------|-------------|
| item | 商品 | SrmMalItemMdPO |
| mall | 商城 | MallProductPO |
| article | 文章 | SrmMalMiscArticlePO |
| basic | 基础配置 | GenMerMerchantMdPO |
| trade | 交易 | MalTradeOrderHeadTrPO |
| retail | 零售 | MalRetailOrderHeaderTrPO |
| commodity | 商品中心 | MalCommodityMdPO |
| mat | 物料管理 | SrmMatManagementTrPO |
| reuse | 利旧管理 | ReuseOrderHeaderTrPO |

## 探测流程总结

1. **Glob 查找 SPI 模块** → `{project}-spi/`
2. **读取一个 PO 文件** → 确认 package 结构和 business domain
3. **Glob 查找所有模块** → 列出可用 modules
4. **向用户报告** → 等待确认或包路径输入
5. **生成代码** → 使用确认的结构信息

这个探测流程确保 skill 能够在生成代码前自动理解项目的包结构，避免硬编码路径。