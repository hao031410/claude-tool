# EMP 工时 Skill 接口参数手册

更新时间：2026-02-25  
适用域名：`https://emp-portal.app.duandian.com`

## -1. 渐进加载建议（先读最小集）

1. 首次执行只读以下章节：
   - `0. 按执行阶段索引`
   - `1. 通用规范`
   - `5.12 WORKTIME$work_hour_filling`
   - `6. 异常码与处理规范`
2. 仅在对应阶段再按需读取其他接口章节，避免一次性加载全部细节。

## 0. 按执行阶段索引（推荐读取顺序）

1. 初始化与鉴权：
   - `GET /iam/api/v1/user/login/prepare`
   - `POST /iam/api/v1/user/login/account`
   - `GET /iam/api/v1/user/login/redirect-url`
   - `MD$query_current_login_related_employee_info`
2. 执行前校验：
   - `WORKTIME$get_employee_monthly_work_status_detail`
   - `MD$get_holidays_no_makeup`
   - `MD$get_employee_leave_info`
   - `WORKTIME$check_employee_department_working_hours_continuity`
   - `WORKTIME$get_workday_by_employee_and_workhour_type`
3. 项目装载与配置校验：
   - `WORKTIME$get_user_current_projects`
   - `WORKTIME$query_subproject_details`
   - `WORKTIME$get_assigned_project_employee_working_hours`
   - `WORKTIME$get_employee_free_working_hours`
4. 写入与回查：
   - `WORKTIME$work_hour_filling`
   - `WORKTIME$get_project_detail_work_hours`
5. 驳回处理：
   - `WORKTIME$reject_resubmit_work_hours`
6. 元数据校验（按需）：
   - `/api/trantor/runtime/scene/data-manager/light/WORKTIME$work_time_save_list?...`
   - `/api/trantor/runtime/scene/data-manager/view-permission/WORKTIME$work_time_save_list:list`

## 1. 通用规范

### 1.0 项目清单展示与用户输入规范
1. 展示样式（缩进）：
```text
- DEPARTMENT / 186029 / 开发一组
  - RECRUIT / 招聘
  - PERFORMANCE / 绩效
  - TRAIN / 培训
  - ROUTINE / 日常事务
```
2. 用户选择最小输入（单项目）：
```text
186029 / ROUTINE / 1.0
```
3. 多项目分摊输入（分行）：
```text
186029 / ROUTINE / 0.5
186030 / DEV / 0.5
```
4. 解析规则：
   - 默认按 `projectCode / detailCode / percentage` 解析。
   - `projectType`、`detailName` 由已加载清单补全。
   - 若 `projectCode+detailCode` 匹配不唯一，则回退要求补充 `projectType` 或完整行。
   - 多条 `percentage` 合计必须为 `1.0`。

### 1.1 Base URL 与路径
1. 登录链路：`/iam/api/v1/user/login/*`
2. 场景接口：`/api/trantor/runtime/scene/data-manager/*`
3. 业务接口：`/api/trantor/service/engine/execute/${serviceKey}`

### 1.2 通用 Header（建议）
```http
Accept: application/json, text/plain, */*
Content-Type: application/json
Origin: https://emp-portal.app.duandian.com
Referer: https://emp-portal.app.duandian.com/EMP_MANAGER_PORTAL/EMP_MANAGER_PORTAL/EMP_MANAGER_PORTAL$LrFEow/page?_tab_id=${tabId}&sceneKey=WORKTIME%24work_time_save_list&viewKey=WORKTIME%24work_time_save_list%3Alist
Cookie: emp_cookie=${empCookie}
```

### 1.3 Header 参数说明
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `Accept` | string | 是 | 固定建议值，保证 JSON 响应 |
| `Content-Type` | string | POST 必填 | 建议 `application/json` |
| `Origin` | string | 写接口强制 | 跨域来源，风控会校验 |
| `Referer` | string | 写接口强制 | 建议工时填报页面 URL |
| `Cookie.emp_cookie` | string | 是 | EMP 会话凭据 |

### 1.4 通用响应结构
成功：
```json
{
  "requestId": "${requestId}",
  "success": true,
  "data": {
    "data": {}
  }
}
```

失败：
```json
{
  "requestId": "${requestId}",
  "success": false,
  "err": {
    "code": "${errorCode}",
    "msg": "${errorMessage}"
  }
}
```

### 1.5 占位符字典
| 占位符 | 类型 | 说明 | 来源 |
|---|---|---|---|
| `${empCookie}` | string | EMP 登录态 cookie 值 | 用户提供或登录链路获取 |
| `${staffId}` | long | 员工 ID | `MD$query_current_login_related_employee_info` |
| `${projectType}` | string | 项目类型，如 `DEPARTMENT` | 项目列表接口 |
| `${projectCode}` | string | 项目编码 | 项目列表接口 |
| `${projectName}` | string | 项目名称 | 项目列表接口 |
| `${detailCode}` | string | 子项目编码 | 子项目接口 |
| `${detailName}` | string | 子项目名称 | 子项目接口 |
| `${fillDate}` | string | `YYYY-MM-DD 00:00:00` | 任务日期（上海时区） |
| `${percentage}` | number | 0~1，小数 | 项目配置 |
| `${yyyy-MM}` | string | 月份，如 `2026-02` | 执行上下文 |
| `${yyyy-MM-dd}` | string | 日期，如 `2026-02-25` | 执行上下文 |
| `${tabId}` | string | 页面 tab id（可选） | 前端页面参数 |

### 1.6 时间戳规则（强制）
1. 所有 `beginDate/endDate` 使用毫秒时间戳（13位）。
2. 按 `Asia/Shanghai` 计算目标日：
   - `beginDate` = 当天 `00:00:00.000`
   - `endDate` = 当天 `23:59:59.999`
3. 禁止将 `endDate` 误设为次日 `00:00:00.000`，否则会跨日导致校验与填报错位。

## 2. 登录链路

### 2.1 GET `/iam/api/v1/user/login/prepare`
用途：获取登录准备参数（盐值/验证码要求）。

请求头：参考通用 Header（可不带 cookie）。

响应样例：
```json
{
  "success": true,
  "data": {
    "salt": "${salt}",
    "captchaRequired": false
  }
}
```

### 2.2 POST `/iam/api/v1/user/login/account`
用途：账号登录，建立会话。

请求体样例：
```json
{
  "account": "${phoneOrEmail}",
  "password": "${encryptedPassword}",
  "captcha": "${captchaIfAny}"
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `account` | string | 是 | 手机号或邮箱 |
| `password` | string | 是 | 前端加密后的密码 |
| `captcha` | string | 条件必填 | 出现验证码时必填 |

### 2.3 GET `/iam/api/v1/user/login/redirect-url`
用途：获取登录后跳转地址。

响应样例：
```json
{
  "success": true,
  "data": {
    "redirectUrl": "${redirectUrl}"
  }
}
```

## 3. 场景元数据接口

### 3.1 GET `/api/trantor/runtime/scene/data-manager/light/WORKTIME$work_time_save_list?view=WORKTIME$work_time_save_list:list`
用途：读取视图与服务映射。

### 3.2 GET `/api/trantor/runtime/scene/data-manager/view-permission/WORKTIME$work_time_save_list:list`
用途：读取当前账号可执行权限。

## 4. Service Engine 统一调用

请求路径：
`POST /api/trantor/service/engine/execute/${serviceKey}`

通用 body 壳：
```json
{
  "params": {
    "req": {}
  }
}
```

## 5. 业务接口明细（Skill 全覆盖）

### 5.1 `MD$query_current_login_related_employee_info`
用途：获取当前登录员工信息与主部门。

请求体：
```json
{
  "params": {}
}
```

响应关键字段：
| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data.data.id` | long | 员工 ID（`staffId`） |
| `data.data.name` | string | 员工姓名 |
| `data.data.phone` | string | 手机号 |
| `data.data.mainDept.id` | long | 主部门项目编码候选 |

### 5.2 `WORKTIME$get_user_current_projects`
用途：获取当前可填报项目列表。

请求体（推荐，必须带时间范围）：
```json
{
  "params": {
    "req": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs}
    }
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `beginDate` | long | 是 | 查询区间开始时间戳（毫秒） |
| `endDate` | long | 是 | 查询区间结束时间戳（毫秒） |

响应关键字段：
| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data.data[].projectCode` | string | 项目编码 |
| `data.data[].type` | string | 项目类型 |
| `data.data[].name` | string | 项目名称 |

异常样例：
```json
{
  "success": false,
  "err": {
    "code": "V0311",
    "msg": "Extension service 'WORK_TIME_GET_PROJECT_STAFF_IS_PRESENT_IN' execution exception"
  }
}
```

执行规则（必须）：
1. 先调用本接口拉取全部项目；
2. 对每个项目再调用 `WORKTIME$query_subproject_details` 拉取子项目；
3. 合并成“项目+子项目”候选清单后再让用户选择；
4. 若 `project_config` 缺失且本接口返回空列表，直接提示并中断填报，不调用写接口。

### 5.3 `WORKTIME$query_subproject_details`
用途：获取指定项目下可填报细项。

请求体：
```json
{
  "params": {
    "req": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs},
      "baseProjectReq": {
        "type": "${projectType}",
        "projectCode": "${projectCode}"
      }
    }
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `beginDate` | long | 是 | 查询区间开始时间戳（毫秒） |
| `endDate` | long | 是 | 查询区间结束时间戳（毫秒） |
| `baseProjectReq.type` | string | 是 | 项目类型 |
| `baseProjectReq.projectCode` | string | 是 | 目标项目编码 |

响应关键字段：
| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data.data[].detailCode` | string | 子项目编码 |
| `data.data[].name` | string | 子项目名称 |

### 5.4 `WORKTIME$get_employee_monthly_work_status_detail`
用途：查询某月每日填报状态。

请求体（页面真实请求）：
```json
{
  "params": {
    "req": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs}
    }
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `beginDate` | long | 是 | 查询区间开始时间戳（毫秒） |
| `endDate` | long | 是 | 查询区间结束时间戳（毫秒） |

响应关键字段：
| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data.data[].date` | string | 日期（`YYYY-MM-DD 00:00:00`） |
| `data.data[].reportingStatus` | string | 如 `FULL/UNDER_FILL/NOT_FILL_OUT/PENDING_FILL/LEAVE` |
| `data.data[].percentage` | number | 当日已填比例 |
| `data.data[].duration` | number | 时长/天数信息（请假等场景） |

失败样例：
```json
{
  "success": false,
  "err": {
    "msg": "查询失败，时间范围不允许为空"
  }
}
```

### 5.5 `MD$get_employee_leave_info`
用途：查询请假区间，过滤无需填报日期。

请求体：
```json
{
  "params": {
    "date_range": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs},
      "staffBOS": [
        {
          "id": ${staffId}
        }
      ]
    }
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `date_range.beginDate` | long | 是 | 查询区间开始时间戳（毫秒） |
| `date_range.endDate` | long | 是 | 查询区间结束时间戳（毫秒） |
| `date_range.staffBOS[]` | array | 是 | 员工对象数组（页面实测传完整 staff 对象） |

响应关键字段：
| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data.data[].leaveDate` | string | 请假日期 |
| `data.data[].leaveType` | string | 请假类型 |

### 5.6 `MD$get_holidays_no_makeup`
用途：查询法定假期，过滤无需填报日期。

请求体：
```json
{
  "params": {
    "beginDate": ${beginDateMs},
    "endDate": ${endDateMs}
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `beginDate` | long | 是 | 查询区间开始时间戳（毫秒） |
| `endDate` | long | 是 | 查询区间结束时间戳（毫秒） |

响应关键字段：
| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data.data[].calendarTime` | long | 日期时间戳（毫秒） |
| `data.data[].statusDict` | string | 状态字典值（如 `1` 法定假日、`3` 周末） |
| `data.data[].description` | string | 描述（如“法定假日”“周末”） |

### 5.7 `WORKTIME$get_project_detail_work_hours`
用途：回查某项目在某日的细项工时比例。

请求体：
```json
{
  "params": {
    "req": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs},
      "baseProjectTO": {
        "type": "${projectType}",
        "projectCode": "${projectCode}"
      },
      "staffs": [
        {
          "id": ${staffId}
        }
      ]
    }
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `beginDate` | long | 是 | 查询区间开始时间戳（毫秒） |
| `endDate` | long | 是 | 查询区间结束时间戳（毫秒） |
| `baseProjectTO.type` | string | 是 | 项目类型 |
| `baseProjectTO.projectCode` | string | 是 | 项目编码 |
| `staffs[]` | array | 是 | 员工对象数组（页面实测传完整 staff 对象） |

响应关键字段：
| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data.data[].detailCode` | string | 子项目编码 |
| `data.data[].percentage` | string/number | 已填比例 |

### 5.8 `WORKTIME$check_employee_department_working_hours_continuity`
用途：检查部门工时连续性（页面前置校验）。

请求体：
```json
{
  "params": {}
}
```

响应关键字段：
| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data.data` | boolean | 连续性检查结果 |

### 5.9 `WORKTIME$get_workday_by_employee_and_workhour_type`
用途：按员工与工时类型查询工作日集合（页面前置校验）。

请求体：
```json
{
  "params": {
    "req": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs},
      "status": "OTHER"
    }
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `beginDate` | long | 是 | 查询区间开始时间戳（毫秒） |
| `endDate` | long | 是 | 查询区间结束时间戳（毫秒） |
| `status` | string | 是 | 工时类型状态，页面实测包含 `OTHER`、`REJECT` |

### 5.10 `WORKTIME$get_assigned_project_employee_working_hours`
用途：查询员工在项目上的已分配工时（页面联动查询）。

请求体（页面实测）：
```json
{
  "params": {
    "req": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs},
      "staffs": [{ "id": ${staffId} }],
      "baseProjectTOS": [
        {
          "type": "${projectType}",
          "projectCode": "${projectCode}",
          "name": "${projectName}"
        }
      ]
    }
  }
}
```

### 5.11 `WORKTIME$get_employee_free_working_hours`
用途：查询员工可分配剩余工时（页面联动查询）。

请求体：
```json
{
  "params": {
    "beginDate": ${beginDateMs},
    "endDate": ${endDateMs}
  }
}
```

### 5.12 `WORKTIME$work_hour_filling`（核心写接口）
用途：写入工时填报记录。

请求体（推荐模板）：
```json
{
  "params": {
    "req": {
      "key": "${staffId}#${projectType}#${projectCode}#${detailCode}",
      "parentKey": "${staffId}#${projectType}#${projectCode}",
      "fillDate": "${fillDate}",
      "percentage": ${percentage},
      "baseProjectTO": {
        "type": "${projectType}",
        "projectCode": "${projectCode}"
      },
      "baseProjectDetailTO": {
        "projectCode": "${projectCode}",
        "detailCode": "${detailCode}",
        "name": "${detailName}"
      }
    }
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string | 建议 | 行键，格式 `${staffId}#${projectType}#${projectCode}#${detailCode}` |
| `parentKey` | string | 建议 | 父键，格式 `${staffId}#${projectType}#${projectCode}` |
| `fillDate` | string | 是 | 填报日期，格式 `YYYY-MM-DD 00:00:00` |
| `percentage` | number | 是 | 填报比例，范围 `0~1` |
| `baseProjectTO.type` | string | 是 | 项目类型 |
| `baseProjectTO.projectCode` | string | 是 | 项目编码 |
| `baseProjectDetailTO.projectCode` | string | 建议 | 细项归属项目编码 |
| `baseProjectDetailTO.detailCode` | string | 建议 | 子项目编码 |
| `baseProjectDetailTO.name` | string | 建议 | 子项目名称 |

约束：
1. 同日多条填报 `percentage` 合计必须 `1.0`。
2. 禁止混用旧字段：`workDate`、`ratio`。
3. 写接口建议固定携带 `Origin/Referer`。

成功样例：
```json
{
  "success": true,
  "data": {
    "data": true
  }
}
```

风控失败样例：
```json
{
  "success": false,
  "err": {
    "code": "非常规操作，请走页面填报~~"
  }
}
```

### 5.13 `WORKTIME$reject_resubmit_work_hours`
用途：驳回后重新提报。

状态说明：
1. 当前版本未抓到页面真实请求（本轮抓包未出现该接口调用）。
2. 暂不纳入自动执行链路。
3. 后续在“驳回后点击重新提报”的真实场景抓包后再补全精确入参/出参。

请求体：
```json
{
  "params": {
    "req": {
      "workDate": "${yyyy-MM-dd 00:00:00}"
    }
  }
}
```

参数说明：
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `workDate` | string | 是 | 需要重新提报的日期 |

## 6. 异常码与处理规范

1. `401/403`：cookie 失效，请求新 cookie 或走登录链路。
2. `V0311`：后端扩展服务异常，记录 `requestId`，降级人工配置。
3. `非常规操作，请走页面填报~~`：风控拦截，禁止重试，切页面自动化。
4. `时间范围不允许为空`：请求体缺少时间参数，补齐时间范围字段。
