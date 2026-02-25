# EMP 工时 API 映射（仅接口定义）

更新时间：2026-02-25  
适用域名：
- 业务接口：`https://emp-portal.app.duandian.com`
- 鉴权接口（`/iam/...` 前缀）：`https://emp-portal-iam.app.duandian.com`

## 1. 通用约定

### 1.1 Base URL
- 业务接口 Base URL：`https://emp-portal.app.duandian.com`
- IAM 鉴权 Base URL：`https://emp-portal-iam.app.duandian.com`

### 1.2 通用 Header
```http
Accept: application/json, text/plain, */*
Content-Type: application/json
Cookie: emp_cookie=${empCookie}
Origin: https://emp-portal.app.duandian.com
Referer: https://emp-portal.app.duandian.com/EMP_MANAGER_PORTAL/EMP_MANAGER_PORTAL/EMP_MANAGER_PORTAL$LrFEow/page?sceneKey=WORKTIME%24work_time_save_list
```

说明：
- `Origin/Referer` 对写接口（如 `WORKTIME$work_hour_filling`）建议固定携带。
- 所有 `beginDate/endDate` 为 13 位毫秒时间戳。
- 规则：凡 URL 路径前缀为 `/iam/...`，必须使用 IAM 域名 `https://emp-portal-iam.app.duandian.com`。

### 1.3 统一业务接口入口
- `POST /api/trantor/service/engine/execute/${serviceKey}`
- 通用请求体外壳：
```json
{
  "params": {
    "req": {}
  }
}
```

### 1.4 统一响应结构
成功：
```json
{
  "requestId": "xxx",
  "success": true,
  "data": {
    "data": {}
  }
}
```

失败：
```json
{
  "requestId": "xxx",
  "success": false,
  "err": {
    "code": "ERROR_CODE",
    "msg": "error message"
  }
}
```

## 2. 鉴权接口

### 2.1 GET `/iam/api/v1/user/login/prepare`
用途：登录前准备参数（如盐值/验证码要求）。

关键返回：
- `data.salt`
- `data.captchaRequired`

### 2.2 POST `/iam/api/v1/user/login/account`
用途：账号登录建立会话。
脚本约定：若传入明文密码，先用 `sha256(password + salt)`（`salt` 来自 prepare）再提交；若已是加密值则直接提交。

请求体：
```json
{
  "account": "${phoneOrEmail}",
  "password": "${encryptedPassword}",
  "captcha": "${captchaIfAny}"
}
```

### 2.3 GET `/iam/api/v1/user/login/redirect-url`
用途：登录后跳转地址。

## 3. 工时填报核心接口

### 3.1 `MD$query_current_login_related_employee_info`
用途：获取当前登录员工信息。

请求体：
```json
{
  "params": {}
}
```

关键返回：
- `data.data.id`：`staffId`
- `data.data.mainDept.id`

### 3.2 `WORKTIME$get_user_current_projects`
用途：拉取当前可填报项目列表。
时间窗约束：`beginDate/endDate` 使用目标日期所在周（周一 00:00:00.000 ~ 周日 23:59:59.999）。

请求体：
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

关键返回：
- `data.data[].projectCode`
- `data.data[].type`
- `data.data[].name`

### 3.3 `WORKTIME$query_subproject_details`
用途：拉取项目下子项目列表。
时间窗约束：与 `WORKTIME$get_user_current_projects` 保持一致，使用目标日期所在周。

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

关键返回：
- `data.data[].detailCode`
- `data.data[].name`

### 3.4 `WORKTIME$work_hour_filling`
用途：写入工时填报记录。

请求体：
```json
{
  "params": {
    "req": {
      "key": "${staffId}#${projectType}#${projectCode}#${detailCode}",
      "parentKey": "${staffId}#${projectType}#${projectCode}",
      "fillDate": "${yyyy-MM-dd 00:00:00}",
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

约束：
- 同日多条 `percentage` 合计必须为 `1.0`。
- `percentage` 范围应为 `0~1`。

### 3.5 `WORKTIME$get_project_detail_work_hours`
用途：按项目+员工回查当日细项工时比例。

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

关键返回：
- `data.data[].detailCode`
- `data.data[].percentage`

## 4. 执行前校验/统计常用接口

### 4.1 `MD$get_holidays_no_makeup`
用途：节假日/周末判定。

请求体：
```json
{
  "params": {
    "beginDate": ${beginDateMs},
    "endDate": ${endDateMs}
  }
}
```

关键返回：
- `data.data[].calendarTime`
- `data.data[].statusDict`（如 `1` 法定假日，`3` 周末）

### 4.2 `MD$get_employee_leave_info`
用途：请假判定。

请求体：
```json
{
  "params": {
    "date_range": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs},
      "staffBOS": [
        {
          "id": ${staffId},
          "jobNumber": "${jobNumber}",
          "name": "${staffName}"
        }
      ]
    }
  }
}
```

约束：
- 必须使用 `params.date_range`，否则可能返回 `V0300: 参数'date_range'不能为空`。
- `staffBOS` 建议直接复用 `MD$query_current_login_related_employee_info` 返回的员工对象（最稳）。

### 4.3 `WORKTIME$get_employee_monthly_work_status_detail`
用途：查询某月每日填报状态。

请求体：
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

关键返回：
- `data.data[].date`
- `data.data[].reportingStatus`
- `data.data[].percentage`

### 4.4 `WORKTIME$check_employee_department_working_hours_continuity`
用途：部门工时连续性校验。

请求体：
```json
{
  "params": {}
}
```

### 4.5 `WORKTIME$get_workday_by_employee_and_workhour_type`
用途：按员工和工时类型查询工作日集合。

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

### 4.6 `WORKTIME$get_assigned_project_employee_working_hours`
用途：查询员工在项目上的已分配工时。

请求体：
```json
{
  "params": {
    "req": {
      "beginDate": ${beginDateMs},
      "endDate": ${endDateMs},
      "staffs": [
        {
          "id": ${staffId}
        }
      ],
      "baseProjectTOS": [
        {
          "type": "${projectType}",
          "projectCode": "${projectCode}"
        }
      ]
    }
  }
}
```

### 4.7 `WORKTIME$get_employee_free_working_hours`
用途：查询员工剩余可分配工时。

请求体：
```json
{
  "params": {
    "beginDate": ${beginDateMs},
    "endDate": ${endDateMs}
  }
}
```

## 5. 常见错误码
- `401/403`：鉴权失效。
- `V0311`：后端扩展服务异常。
- `非常规操作，请走页面填报~~`：风控拦截。
- `时间范围不允许为空`：`beginDate/endDate` 缺失。
