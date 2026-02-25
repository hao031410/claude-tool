---
name: terminus-emp-skill
description: 当用户提到“填工时/工时填报/补工时/工时统计/工时周报/月报”时使用。用于 EMP 工时填报：鉴权、项目校验、按比例写入、写后回查，并输出日/周/月统计（不负责定时调度）。
---

# Terminus EMP Skill

用于 OpenClaw 的 EMP 工时填报技能规范（脚本优先）。

## 1. 使用范围
1. 触发词：`填工时`、`工时填报`、`补工时`、`工时统计`、`工时周报`、`工时月报`。
2. 反例词：`只查询项目`、`仅查看`、`不填报`（命中后不进入写入）。
3. 仅处理填报与统计，不处理定时调度。

## 2. 执行原则（强制）
1. 优先必要参数校验，再执行脚本。
2. 缺 `auth` 时，只索取 cookie/账密，禁止先索要分摊配置。
3. 有 `auth` 但缺 `project_config` 时，先输出项目树形清单，再让用户选择。
4. 未展示项目清单前，禁止要求用户直接提供 `projectCode/detailCode`。
5. 项目清单为空且无缓存配置时，中断并返回原因。
6. 写入前必须校验 `project_config` 字段完整且 `percentage` 合计为 `1.0`。
7. 所有写入需先通过参数校验，禁止“边试边写”。
8. 写入失败时只通知用户失败原因与 `requestId`，由用户自行决定后续操作。
9. 写入失败后禁止自动改配置、禁止自动重试写接口、禁止自动推测替代方案。

项目清单输出模板（强制）：
```text
可填项目清单：
[项目] DEPARTMENT / 186029 / 开发一组
  ├─ ROUTINE / 日常事务
  ├─ TRAIN / 培训
  └─ OPERATION / 运营
```

## 3. 脚本入口
1. 脚本：`scripts/fill_worktime.py`
2. 命令：
   - `list-projects`：拉项目+子项目清单
   - `fill-day`：按配置填报
   - `verify-day`：按配置回查
3. 推荐流程：`list-projects -> 用户确认配置 -> fill-day --verify`

## 4. 文档索引
1. 执行规范与交互模板：`references/spec.md`
2. 持久化定义：`references/persistence.md`
3. 接口定义（仅 API）：`references/api-map.md`
