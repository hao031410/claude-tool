# EMP 工时执行规范

更新时间：2026-02-25

## 1. 输入输出契约

### 1.1 必要输入
1. `auth.emp_cookie`（优先）或可用登录凭据。
2. `targetDate`，格式 `YYYY-MM-DD`；缺省为 `Asia/Shanghai` 当天。
3. `project_config[]`（可来自用户输入或缓存）：
   - `projectType`
   - `projectCode`
   - `detailCode`
   - `percentage`
4. 多条 `percentage` 合计必须为 `1.0`。

### 1.2 输出结果
1. `fill_result`：成功/失败、requestId、失败原因。
2. `stats_result.day`：当天填报结果。
3. `stats_result.week`：周聚合结果。
4. `stats_result.month`：月聚合结果。

## 2. 执行顺序（强制）
1. 加载本地缓存。
2. 必要参数校验（阻断式）。
3. 缺配置时先拉项目清单并展示。
4. 用户确认配置后再次校验。
5. 执行写入。
6. 写后回查。
7. 统计输出并持久化。

## 3. 交互约束（强制）
1. 缺 `auth` 时，不得先索要分摊配置。
2. 缺 `project_config` 时，必须先展示项目树形清单。
3. 未展示清单前，禁止要求用户直接给 `projectCode/detailCode`。
4. 清单为空且无缓存配置时，直接中断，不调用写接口。

项目清单模板：
```text
可填项目清单：
[项目] DEPARTMENT / 186029 / 开发一组
  ├─ ROUTINE / 日常事务
  ├─ TRAIN / 培训
  └─ OPERATION / 运营
```

用户选择模板：
```text
186029 / ROUTINE / 1.0
```

多项目模板：
```text
186029 / ROUTINE / 0.5
186030 / DEV / 0.5
```

## 4. 参数预检规则（阻断式）
1. 认证预检：优先校验 `emp_cookie`；若无效且提供了账密，先自动登录刷新 cookie，再继续。
2. `targetDate` 非法：直接失败。
3. `project_config` 为空：进入“清单展示+选择”流程，不执行写接口。
4. `project_config` 字段缺失：直接失败。
5. `percentage` 非法或合计不为 `1.0`：直接失败。
6. `projectCode/detailCode` 不在当前清单：直接失败。
7. 若 cookie 无效且无可用账密，直接失败，不得发起 `WORKTIME$work_hour_filling`。
8. 任一预检失败时，不得发起 `WORKTIME$work_hour_filling`。

## 5. 异常处理
前置路由约束：
1. 所有 `/iam/...` 接口必须请求 IAM 域名 `https://emp-portal-iam.app.duandian.com`。

异常处理：
1. `401/403`：最多重试 1 次，失败终止。
2. 网络或 `5xx`：指数退避重试 2~3 次。
3. `V0311`：记录 requestId，返回人工处理提示。
4. `非常规操作，请走页面填报~~`：立即终止，不重试。
5. 回查不一致：标记“写入未知态”，要求人工复核。
6. 写接口失败时必须通知用户失败原因和 `requestId`。
7. 写接口失败后不自动改配置，不自动重试写接口，不自动给替代填报方案。

## 6. 统计口径
1. 日统计：`date/reportingStatus/details/lastSuccessAt/sourceRequestId`。
2. 周统计：周一到周日，`cutoffDate=min(weekEnd,today)`，未来日期不计。
3. 月统计：自然月，`cutoffDate=min(monthEnd,today)`，未来日期不计。
4. 应填过滤：排除法定假日、周末、请假日。
