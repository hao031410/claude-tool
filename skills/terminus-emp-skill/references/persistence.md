# EMP 工时持久化定义

更新时间：2026-02-25

## 1. 文件路径
- `${LOCAL_DB_DIR:-~/data}/terminus-emp-skill/config.json`（`auth` + `project_config`）
- `${LOCAL_DB_DIR:-~/data}/terminus-emp-skill/records.json`（`stats_cache`）

## 2. 写入时机
1. 启动时读取（恢复会话与配置）。
2. cookie 更新后写入 `config.json`。
3. 项目配置更新后写入 `config.json`。
4. 填报成功并生成统计后写入 `records.json`（并同步更新 `config.json` 的认证配置）。

## 3. 结构定义
`config.json`：
```json
{
  "auth": {
    "emp_cookie": "${empCookie}",
    "updatedAt": "${isoDatetime}",
    "account": "${accountOptional}",
    "password": "${passwordOrEncryptedPasswordOptional}",
    "passwordEncrypted": false
  },
  "project_config": [
    {
      "projectType": "DEPARTMENT",
      "projectCode": "186029",
      "detailCode": "ROUTINE",
      "detailName": "日常事务",
      "percentage": 1.0,
      "lastVerifiedAt": "${isoDatetime}"
    }
  ]
}
```

`records.json`：
```json
{
  "daily": {},
  "weekly": {},
  "monthly": {}
}
```

## 4. 写入要求
1. 原子写：`*.json.tmp -> rename -> *.json`。
2. 文件权限：`600`。
3. 写入失败时不得覆盖旧文件。

## 5. 字段口径
1. `auth.emp_cookie`：当前可用会话 cookie。
2. `auth.account/password/passwordEncrypted`：可选登录凭据（用于 cookie 失效时自动登录刷新）。
3. `project_config`：最近一次验证通过的分摊配置。
4. `records.daily[yyyy-MM-dd]`：
   - `status`
   - `details`
   - `ratio`
   - `lastSuccessAt`
   - `sourceRequestId`
5. `records.weekly[yyyy-WW]`：
   - `workdayCount`
   - `filledDays`
   - `fillRate`
   - `missing`
6. `records.monthly[yyyy-MM]`：
   - `workdayCount`
   - `filledDays`
   - `fillRate`
   - `summaryByProject`
