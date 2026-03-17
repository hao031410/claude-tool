# 外部模型查询指南

> 知识库结构定义和使用方法

## ⚠️ 强制记录原则

**知识库记录不是可选操作，是强制性要求。**

任何涉及外部模型信息的操作必须同步更新知识库文件 `dependency-knowledge.json`。

## 知识库结构

**存储位置**：`<project-root>/.claude/terp-developer/knowledge/dependency-knowledge.json`

**JSON结构**：
```json
{
  "projectName": "erp-sett",
  "version": "2.0.0.2511.ZYXH.DEV-SNAPSHOT",
  "dependencies": {
    "erp-fin-common-spi": {
      "module": "erp-fin-common-spi",
      "description": "财务通用模型定义",
      "type": "internal",
      "lastUsed": "2026-03-05",
      "useCount": 1
    }
  },
  "externalModels": {
    "GEN_MD$org_struct_md": {
      "module": "erp-master-data",
      "description": "组织结构主数据",
      "type": "external",
      "usageFields": {
        "SettDocTrPO": ["com_org_id", "pur_sls_org_id"]
      },
      "commonFields": {
        "org_code": "组织编码",
        "org_name": "组织名称",
        "org_type": "组织类型"
      },
      "lastUsed": "2026-03-05",
      "useCount": 1
    }
  }
}
```

## 强制更新触发时机

**必须更新知识库的操作：**

1. ✅ **模型创建/更新时** - JSON → PO 转换
   - 提取所有 OBJECT 类型字段的 relationMeta
   - 识别外部模型（relationModelAlias）
   - 记录新模型或更新 usageFields

2. ✅ **模型导出时** - PO → JSON 转换
   - 解析所有 @TableField 关联字段
   - 提取外部模型信息
   - 更新 useCount 和 lastUsed

3. ✅ **模型查询时** - 使用外部模型
   - 通过知识库查询到模型信息
   - 递增 useCount
   - 更新 lastUsed 为当天日期

4. ✅ **项目初始化时** - `-init` 命令
   - 扫描 pom.xml 识别依赖
   - 初始化知识库结构
   - 记录 Maven 配置记忆

## 更新流程（强制执行）

```markdown
1. Read dependency-knowledge.json（如不存在则初始化）
2. 提取外部模型信息：
   - 模型别名（relationModelAlias）
   - 来源模块（从 pom.xml 或已知信息）
   - 当前使用的字段名
3. 更新 externalModels 部分：
   情况A - 新模型：
   ```json
   {
     "GEN_MD$new_model": {
       "module": "erp-xxx",
       "description": "模型含义",
       "type": "external",
       "usageFields": {
         "当前PO": ["字段1", "字段2"]
       },
       "commonFields": {},
       "lastUsed": "2026-03-05",
       "useCount": 1
     }
   }
   ```

   情况B - 已有模型：
   - 添加新的 usageFields（如果字段未记录）
   - useCount 递增
   - lastUsed 更新为当天日期

## relationMeta 补全引导 ⚠️

当识别到 `OBJECT` 类型但缺乏明确 `relationMeta` 时，必须按照以下优先级进行补全：

1. **精准匹配**：
   - 检查同一项目中其他 PO 是否已关联该模型。
   - 参考 `dependency-knowledge.json` 中的 `usageFields`。

2. **基于命名的预测**：
   - `after_sale_id` -> `GEN_MD$after_sale_md`
   - `trade_order_id` -> `GEN_MD$trade_order_md`
   - `sku_id` -> `GEN_MD$sku_md`

3. **默认关联字段**：
   - `relationFieldKey`：默认设为 `id`。
   - `displayFieldKey`：优先搜索 `code` 或 `name` 结尾的字段，无则设为 `id`。

4. **输出确认**：
   - 在生成 JSON 时，对于预测生成的 `relationMeta`，必须附加 `// ⚠️ 请确认关联模型别名是否正确` 的注释。

---

4. Write 更新后的 dependency-knowledge.json
5. 向用户确认记录完成

⚠️ 禁止行为：
- ❌ 导出/修改模型后不更新知识库
- ❌ 只记录部分外部模型，遗漏 relationMeta 关联
- ❌ 跳过 useCount 和 lastUsed 更新
- ❌ 记录失败时继续执行后续步骤
```

## 查询复用

**使用场景**：
```java
// 用户询问：如何查询商品信息？

// 1. Read dependency-knowledge.json
// 2. 检索到 MalCommodityMdPO
// 3. 返回常用查询方法 + 更新 useCount

建议查询方式：
- findByCode: 根据商品编码查询
- findByIds: 批量查询商品

示例代码：
malCommodityMdRepo.selectOne(new LambdaQueryWrapper<MalCommodityMdPO>()
    .eq(MalCommodityMdPO::getCommodityCode, code))

// 4. 更新 useCount 和 lastUsed
```

## Maven配置记忆

**存储位置**：`<project-root>/.claude/terp-developer/knowledge/maven-config.json`

**JSON结构**：
```json
{
  "mavenVersion": "3.x",
  "javaVersion": "17",
  "projectRoot": "/path/to/project",
  "parent": {
    "groupId": "io.terminus.erp",
    "artifactId": "erp-parent",
    "version": "2.0.0.2511.12251749.RELEASE"
  },
  "modules": ["erp-sett-spi", "erp-sett-infrastructure"],
  "buildOrder": "spi → infrastructure → domain → app → adapter → starter",
  "initialized": "2026-03-05"
}
```

**作用**：记录项目依赖和Maven配置路径，避免重复询问