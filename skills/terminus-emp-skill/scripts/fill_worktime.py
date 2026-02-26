#!/usr/bin/env python3
"""
EMP 工时填报脚本（最小接口集）。

目标：
1) 直接脚本调用核心接口，减少 LLM 编排耗时。
2) 固定流程：项目列表 -> 填报 -> 回查。
3) 记录每一步接口耗时，便于定位慢点。
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.cookiejar
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_BASE_URL = "https://emp-portal.app.duandian.com"
DEFAULT_IAM_BASE_URL = "https://emp-portal-iam.app.duandian.com"
DEFAULT_REFERER = (
    "https://emp-portal.app.duandian.com/EMP_MANAGER_PORTAL/EMP_MANAGER_PORTAL/"
    "EMP_MANAGER_PORTAL$LrFEow/page?_tab_id=skill-runner&sceneKey=WORKTIME%24work_time_save_list"
    "&viewKey=WORKTIME%24work_time_save_list%3Alist"
)
DEFAULT_IAM_REFERER = (
    "https://emp-portal-iam.app.duandian.com/EMP_MANAGER_PORTAL-EMP-tpf_hkboivmz/login"
)
ASIA_SHANGHAI = ZoneInfo("Asia/Shanghai")
MAX_DATE_DRIFT_DAYS = 7


def default_cache_dir() -> pathlib.Path:
    """默认缓存目录：$LOCAL_DB_DIR/terminus-emp-skill，未设置则 ~/data。"""
    base_dir = pathlib.Path(os.getenv("LOCAL_DB_DIR", "~/data")).expanduser()
    return base_dir / "terminus-emp-skill"


def default_config_state_file() -> pathlib.Path:
    """默认配置缓存文件（auth + project_config）。"""
    return default_cache_dir() / "config.json"


def default_records_state_file() -> pathlib.Path:
    """默认填报记录缓存文件（stats_cache）。"""
    return default_cache_dir() / "records.json"


DEFAULT_CONFIG_STATE_FILE = default_config_state_file()
DEFAULT_RECORDS_STATE_FILE = default_records_state_file()


class EmpClient:
    """EMP API 轻量客户端（service engine）。"""

    def __init__(
        self,
        base_url: str,
        iam_base_url: str,
        emp_cookie: str,
        iam_cookie: str = "",
        iam_referer: str = DEFAULT_IAM_REFERER,
        timeout_seconds: int = 15,
        retries: int = 1,
        backoff_seconds: float = 0.8,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.iam_base_url = iam_base_url.rstrip("/")
        self.emp_cookie = emp_cookie.strip()
        self.iam_cookie = iam_cookie.strip()
        self.iam_referer = iam_referer
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.backoff_seconds = backoff_seconds

    def _extract_emp_cookie_from_headers(self, headers: Any) -> str:
        """从响应头提取 emp_cookie。"""
        if headers is None:
            return ""
        cookie_values = []
        if hasattr(headers, "get_all"):
            cookie_values = headers.get_all("Set-Cookie") or []
        elif isinstance(headers, dict):
            raw = headers.get("Set-Cookie", "")
            cookie_values = [raw] if raw else []
        for raw_cookie in cookie_values:
            # Set-Cookie: emp_cookie=xxx; Path=/; ...
            prefix = "emp_cookie="
            idx = str(raw_cookie).find(prefix)
            if idx >= 0:
                tail = str(raw_cookie)[idx + len(prefix):]
                return tail.split(";", 1)[0].strip()
        return ""

    def _auth_headers(self, for_iam: bool = False) -> dict[str, str]:
        origin = self.iam_base_url if for_iam else DEFAULT_BASE_URL
        referer = self.iam_referer if for_iam else DEFAULT_REFERER
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": origin,
            "Referer": referer,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
            ),
        }
        if for_iam and self.iam_cookie:
            headers["Cookie"] = self.iam_cookie
        return headers

    def _open_json(
        self,
        opener: urllib.request.OpenerDirector,
        url: str,
        method: str,
        body: dict[str, Any] | None = None,
        for_iam: bool = False,
    ) -> tuple[dict[str, Any], Any]:
        payload = None
        if body is not None:
            payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url=url, data=payload, headers=self._auth_headers(for_iam=for_iam), method=method
        )
        with opener.open(req, timeout=self.timeout_seconds) as resp:
            text = resp.read().decode("utf-8")
            parsed = json.loads(text) if text else {}
            return parsed, resp.headers

    def login_and_refresh_cookie(
        self,
        account: str,
        password: str,
        password_encrypted: bool = False,
        captcha: str = "",
    ) -> str:
        """
        使用 IAM 账号登录并刷新 emp_cookie。
        默认按 `sha256(明文密码 + salt)` 生成加密密码；若 `password_encrypted=True` 则直接透传。
        """
        account = account.strip()
        password = password.strip()
        if not account or not password:
            raise RuntimeError("登录失败：account/password 不能为空。")

        jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

        prepare_url = f"{self.iam_base_url}/iam/api/v1/user/login/prepare"
        prepare_data, _ = self._open_json(
            opener=opener, url=prepare_url, method="GET", body=None, for_iam=True
        )
        salt = str((prepare_data.get("data") or {}).get("salt") or "")
        captcha_required = bool((prepare_data.get("data") or {}).get("captchaRequired"))
        if captcha_required and not captcha:
            raise RuntimeError("登录失败：需要验证码 captcha，但未提供。")

        if password_encrypted:
            encrypted_password = password
        else:
            encrypted_password = hashlib.sha256(f"{password}{salt}".encode("utf-8")).hexdigest()

        login_url = f"{self.iam_base_url}/iam/api/v1/user/login/account"
        login_payload = {
            "account": account,
            "password": encrypted_password,
            "captcha": captcha or "",
        }
        login_data, login_headers = self._open_json(
            opener=opener, url=login_url, method="POST", body=login_payload, for_iam=True
        )
        if login_data.get("success") is False:
            err = login_data.get("err") or {}
            raise RuntimeError(
                f"登录失败: code={err.get('code', 'UNKNOWN')}, msg={err.get('msg', 'unknown error')}"
            )

        # 某些网关在 redirect-url 阶段补齐 cookie。
        redirect_url = f"{self.iam_base_url}/iam/api/v1/user/login/redirect-url"
        try:
            self._open_json(opener=opener, url=redirect_url, method="GET", body=None, for_iam=True)
        except Exception:
            # redirect-url 失败不阻断，优先从 jar / login headers 抽取 cookie。
            pass

        fresh_cookie = ""
        for c in jar:
            if c.name == "emp_cookie":
                fresh_cookie = c.value.strip()
                break
        if not fresh_cookie:
            fresh_cookie = self._extract_emp_cookie_from_headers(login_headers)
        if not fresh_cookie:
            raise RuntimeError("登录失败：未拿到 emp_cookie。")

        self.emp_cookie = fresh_cookie
        return fresh_cookie

    def _headers(self, write: bool) -> dict[str, str]:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": f"emp_cookie={self.emp_cookie}",
            "Origin": DEFAULT_BASE_URL,
            "Referer": DEFAULT_REFERER,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
            ),
        }
        if write:
            # 写接口保留同源头，避免风控误判。
            headers["Origin"] = DEFAULT_BASE_URL
            headers["Referer"] = DEFAULT_REFERER
        return headers

    def engine_execute(self, service_key: str, body: dict[str, Any], write: bool = False) -> dict[str, Any]:
        encoded_key = urllib.parse.quote(service_key, safe="$")
        url = f"{self.base_url}/api/trantor/service/engine/execute/{encoded_key}"
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            data=payload,
            headers=self._headers(write=write),
            method="POST",
        )

        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                    text = resp.read().decode("utf-8")
                    parsed = json.loads(text)
                    if parsed.get("success") is not True:
                        err = parsed.get("err") or {}
                        code = err.get("code", "UNKNOWN")
                        msg = err.get("msg", "unknown error")
                        request_id = parsed.get("requestId")
                        raise RuntimeError(
                            f"{service_key} failed: code={code}, msg={msg}, requestId={request_id}"
                        )
                    return parsed
            except RuntimeError:
                # 业务失败（success=false）不重试，避免重复写入或放大错误。
                raise
            except urllib.error.HTTPError as exc:
                last_err = exc
                if write:
                    raise
                if exc.code < 500 or attempt >= self.retries:
                    raise
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_err = exc
                if write:
                    raise
                if attempt >= self.retries:
                    raise
            time.sleep(self.backoff_seconds * (2**attempt))
        assert last_err is not None
        raise last_err


def to_day_range_ms(target_date: str) -> tuple[int, int]:
    """将 YYYY-MM-DD 转换为当天毫秒时间窗。"""
    date_obj = dt.datetime.strptime(target_date, "%Y-%m-%d").date()
    start = dt.datetime.combine(date_obj, dt.time.min, tzinfo=ASIA_SHANGHAI)
    end = dt.datetime.combine(date_obj, dt.time(23, 59, 59, 999000), tzinfo=ASIA_SHANGHAI)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def to_week_range_ms(target_date: str) -> tuple[int, int]:
    """将 YYYY-MM-DD 转换为所在周时间窗（周一00:00:00.000 ~ 周日23:59:59.999）。"""
    date_obj = dt.datetime.strptime(target_date, "%Y-%m-%d").date()
    monday = date_obj - dt.timedelta(days=date_obj.weekday())
    sunday = monday + dt.timedelta(days=6)
    start = dt.datetime.combine(monday, dt.time.min, tzinfo=ASIA_SHANGHAI)
    end = dt.datetime.combine(sunday, dt.time(23, 59, 59, 999000), tzinfo=ASIA_SHANGHAI)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def load_json_file(file_path: pathlib.Path) -> dict[str, Any]:
    """读取 JSON 文件，不存在或结构非法时返回空对象。"""
    if not file_path.exists():
        return {}
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {}
    return data


def load_config_state(config_file: pathlib.Path) -> dict[str, Any]:
    """读取配置缓存（auth + project_config），兼容旧字段。"""
    data = load_json_file(config_file)
    data.setdefault("auth", {})
    # 兼容旧版 state：cookie 在顶层字段。
    legacy_cookie = str(data.get("cookie", "")).strip()
    if legacy_cookie and not str(data["auth"].get("emp_cookie", "")).strip():
        data["auth"]["emp_cookie"] = legacy_cookie
    data.setdefault("project_config", [])
    return data


def load_stats_cache(records_file: pathlib.Path) -> dict[str, Any]:
    """读取填报记录缓存（stats_cache）。"""
    data = load_json_file(records_file)
    data.setdefault("daily", {})
    data.setdefault("weekly", {})
    data.setdefault("monthly", {})
    return data


def save_json_file(file_path: pathlib.Path, data: dict[str, Any]) -> None:
    """原子写入 JSON 文件并收紧权限。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = file_path.with_suffix(".json.tmp")
    with tmp_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.chmod(tmp_file, 0o600)
    tmp_file.replace(file_path)


def save_config_state(config_file: pathlib.Path, state: dict[str, Any]) -> None:
    """仅持久化配置缓存字段，避免与记录缓存混写。"""
    payload = {
        "auth": state.get("auth") or {},
        "project_config": state.get("project_config") or [],
    }
    save_json_file(config_file, payload)


def save_stats_cache(records_file: pathlib.Path, stats_cache: dict[str, Any]) -> None:
    """仅持久化填报记录缓存字段。"""
    payload = {
        "daily": (stats_cache or {}).get("daily") or {},
        "weekly": (stats_cache or {}).get("weekly") or {},
        "monthly": (stats_cache or {}).get("monthly") or {},
    }
    save_json_file(records_file, payload)


def data_list(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """统一抽取 data.data 列表。"""
    data = (raw.get("data") or {}).get("data")
    if isinstance(data, list):
        return data
    return []


def data_obj(raw: dict[str, Any]) -> dict[str, Any]:
    """统一抽取 data.data 对象。"""
    data = (raw.get("data") or {}).get("data")
    if isinstance(data, dict):
        return data
    return {}


def parse_project_config(args: argparse.Namespace, state: dict[str, Any]) -> list[dict[str, Any]]:
    """解析 project_config，优先命令行，回退 state。"""
    if args.config_json:
        cfg = json.loads(args.config_json)
    elif args.config_file:
        with open(args.config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = state.get("project_config") or []
    if not isinstance(cfg, list) or not cfg:
        raise ValueError("project_config 为空，请通过 --config-json/--config-file 提供。")
    ratio_sum = sum(float(i.get("percentage", 0)) for i in cfg)
    if abs(ratio_sum - 1.0) > 1e-6:
        raise ValueError(f"project_config percentage 合计必须为 1.0，当前为 {ratio_sum}")
    required = ("projectType", "projectCode", "detailCode", "percentage")
    for idx, item in enumerate(cfg):
        miss = [k for k in required if k not in item]
        if miss:
            raise ValueError(f"project_config[{idx}] 缺少字段: {','.join(miss)}")
        pct = float(item["percentage"])
        if pct <= 0 or pct > 1:
            raise ValueError(f"project_config[{idx}] percentage 必须在 (0,1]，当前为 {pct}")
    return cfg


def print_project_tree(projects: list[dict[str, Any]], project_details: dict[tuple[str, str], list[dict[str, Any]]]) -> None:
    print("可填项目清单：")
    for p in projects:
        project_type = p.get("type", "")
        project_code = str(p.get("projectCode", ""))
        project_name = p.get("name", "")
        print(f"[项目] {project_type} / {project_code} / {project_name}")
        details = project_details.get((project_type, project_code), [])
        for d in details:
            print(f"  ├─ {d.get('detailCode', '')} / {d.get('name', '')}")


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def default_target_date() -> str:
    """默认目标日期：Asia/Shanghai 当天。"""
    return dt.datetime.now(ASIA_SHANGHAI).date().isoformat()


def resolve_target_date(date_arg: str | None, force_date: bool) -> str:
    """
    解析并校验目标日期：
    1) 未传时使用 Asia/Shanghai 当天；
    2) 默认拒绝未来日期；
    3) 默认拒绝与今天相差超过 MAX_DATE_DRIFT_DAYS 的日期（防止旧参数误注入）；
    4) 通过 --force-date 可放开 2/3。
    """
    today = dt.datetime.now(ASIA_SHANGHAI).date()
    target_raw = (date_arg or "").strip()
    target = today if not target_raw else dt.datetime.strptime(target_raw, "%Y-%m-%d").date()

    drift_days = (target - today).days
    if not force_date:
        if drift_days > 0:
            raise ValueError(
                f"目标日期 {target.isoformat()} 晚于当前上海日期 {today.isoformat()}，"
                "默认禁止未来日期；如需强制执行请加 --force-date。"
            )
        if abs(drift_days) > MAX_DATE_DRIFT_DAYS:
            raise ValueError(
                f"目标日期 {target.isoformat()} 与当前上海日期 {today.isoformat()} 相差 {abs(drift_days)} 天，"
                f"超过保护阈值 {MAX_DATE_DRIFT_DAYS} 天；如需强制执行请加 --force-date。"
            )
    return target.isoformat()


def is_auth_failure(exc: Exception) -> bool:
    """判断异常是否为鉴权失败（cookie 失效）。"""
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in (401, 403)
    msg = str(exc)
    return ("code=401" in msg) or ("code=403" in msg) or ("UNAUTHORIZED" in msg.upper())


def resolve_auth_inputs(
    args: argparse.Namespace, state: dict[str, Any]
) -> tuple[str, str, str, bool, str, str]:
    """按优先级解析认证输入：命令行 > 环境变量 > state。"""
    auth = state.get("auth") or {}
    emp_cookie = (args.cookie or os.getenv("EMP_COOKIE", "") or auth.get("emp_cookie", "")).strip()
    account = (args.account or os.getenv("EMP_ACCOUNT", "") or auth.get("account", "")).strip()
    password = (args.password or os.getenv("EMP_PASSWORD", "") or auth.get("password", "")).strip()
    password_encrypted = bool(args.password_encrypted or auth.get("passwordEncrypted", False))
    captcha = (args.captcha or "").strip()
    iam_cookie = (args.iam_cookie or os.getenv("EMP_IAM_COOKIE", "") or auth.get("iam_cookie", "")).strip()
    return emp_cookie, account, password, password_encrypted, captcha, iam_cookie


def ensure_valid_cookie(
    client: EmpClient,
    args: argparse.Namespace,
    state: dict[str, Any],
    config_file: pathlib.Path,
) -> None:
    """
    启动前保证 cookie 可用：
    1) 优先验证现有 cookie；
    2) cookie 失效且有账密时自动登录刷新；
    3) 刷新后落盘，后续调用统一使用新 cookie。
    """
    _, account, password, password_encrypted, captcha, iam_cookie = resolve_auth_inputs(args, state)
    client.iam_cookie = iam_cookie

    cookie_ok = False
    if client.emp_cookie:
        try:
            client.engine_execute("MD$query_current_login_related_employee_info", {"params": {}})
            cookie_ok = True
        except Exception as exc:
            if not is_auth_failure(exc):
                raise

    if cookie_ok:
        return

    if not account or not password:
        raise RuntimeError("cookie 无效且未提供账密，无法自动登录。")

    client.login_and_refresh_cookie(
        account=account,
        password=password,
        password_encrypted=password_encrypted,
        captcha=captcha,
    )
    # 登录后再做一次探测，确保后续接口稳定。
    client.engine_execute("MD$query_current_login_related_employee_info", {"params": {}})

    state.setdefault("auth", {})
    state["auth"]["emp_cookie"] = client.emp_cookie
    state["auth"]["updatedAt"] = now_iso()
    if account:
        state["auth"]["account"] = account
    if password:
        state["auth"]["password"] = password
        state["auth"]["passwordEncrypted"] = bool(password_encrypted)
    if iam_cookie:
        state["auth"]["iam_cookie"] = iam_cookie
    save_config_state(config_file, state)


def fetch_project_catalog(
    client: EmpClient,
    begin_ms: int,
    end_ms: int,
) -> tuple[list[dict[str, Any]], dict[tuple[str, str], list[dict[str, Any]]], list[dict[str, Any]]]:
    """拉取项目和子项目清单，并返回耗时明细。"""
    timings: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    projects_raw = client.engine_execute(
        "WORKTIME$get_user_current_projects",
        {"params": {"req": {"beginDate": begin_ms, "endDate": end_ms}}},
    )
    timings.append({"service": "WORKTIME$get_user_current_projects", "ms": round((time.perf_counter() - t0) * 1000, 2)})
    projects = data_list(projects_raw)

    detail_map: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for p in projects:
        p_type = p.get("type")
        p_code = str(p.get("projectCode"))
        t1 = time.perf_counter()
        details_raw = client.engine_execute(
            "WORKTIME$query_subproject_details",
            {
                "params": {
                    "req": {
                        "beginDate": begin_ms,
                        "endDate": end_ms,
                        "baseProjectReq": {"type": p_type, "projectCode": p_code},
                    }
                }
            },
        )
        timings.append({"service": "WORKTIME$query_subproject_details", "projectCode": p_code, "ms": round((time.perf_counter() - t1) * 1000, 2)})
        detail_map[(str(p_type), p_code)] = data_list(details_raw)
    return projects, detail_map, timings


def validate_config_against_catalog(
    cfg: list[dict[str, Any]],
    projects: list[dict[str, Any]],
    detail_map: dict[tuple[str, str], list[dict[str, Any]]],
) -> None:
    """校验 project_config 是否在当前项目清单中。"""
    project_keys = {(str(p.get("type")), str(p.get("projectCode"))) for p in projects}
    for idx, item in enumerate(cfg):
        p_type = str(item["projectType"])
        p_code = str(item["projectCode"])
        d_code = str(item["detailCode"])
        if (p_type, p_code) not in project_keys:
            raise ValueError(f"project_config[{idx}] 项目不存在: {p_type}/{p_code}")
        details = detail_map.get((p_type, p_code), [])
        detail_codes = {str(d.get("detailCode")) for d in details}
        if d_code not in detail_codes:
            raise ValueError(f"project_config[{idx}] 子项目不存在: {p_type}/{p_code}/{d_code}")


def run_list_projects(client: EmpClient, target_date: str, as_json: bool) -> int:
    begin_ms, end_ms = to_week_range_ms(target_date)
    projects, detail_map, timings = fetch_project_catalog(client, begin_ms, end_ms)

    if as_json:
        result = {
            "date": target_date,
            "projectCount": len(projects),
            "projects": projects,
            "projectDetails": {
                f"{k[0]}#{k[1]}": v for k, v in detail_map.items()
            },
            "timings": timings,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_project_tree(projects, detail_map)
        print("\n接口耗时(ms):")
        for item in timings:
            desc = item["service"]
            if "projectCode" in item:
                desc += f"({item['projectCode']})"
            print(f"- {desc}: {item['ms']}")
    return 0


def run_fill_day(
    client: EmpClient,
    state: dict[str, Any],
    config_file: pathlib.Path,
    records_file: pathlib.Path,
    target_date: str,
    args: argparse.Namespace,
) -> int:
    begin_ms, end_ms = to_day_range_ms(target_date)
    week_begin_ms, week_end_ms = to_week_range_ms(target_date)
    fill_date = f"{target_date} 00:00:00"
    cfg = parse_project_config(args, state)

    timings: list[dict[str, Any]] = []
    # 先做项目配置有效性校验，校验通过后才进入写接口。
    projects, detail_map, catalog_timings = fetch_project_catalog(client, week_begin_ms, week_end_ms)
    timings.extend(catalog_timings)
    validate_config_against_catalog(cfg, projects, detail_map)

    t0 = time.perf_counter()
    staff_raw = client.engine_execute("MD$query_current_login_related_employee_info", {"params": {}})
    timings.append({"service": "MD$query_current_login_related_employee_info", "ms": round((time.perf_counter() - t0) * 1000, 2)})
    staff = data_obj(staff_raw)
    staff_id = staff.get("id")
    if staff_id is None:
        raise RuntimeError("未获取到 staffId，无法构造填报 key。")

    request_ids: list[str] = []
    for item in cfg:
        project_type = str(item["projectType"])
        project_code = str(item["projectCode"])
        detail_code = str(item["detailCode"])
        detail_name = str(item.get("detailName", detail_code))
        percentage = float(item["percentage"])

        body = {
            "params": {
                "req": {
                    "key": f"{staff_id}#{project_type}#{project_code}#{detail_code}",
                    "parentKey": f"{staff_id}#{project_type}#{project_code}",
                    "fillDate": fill_date,
                    "percentage": percentage,
                    "baseProjectTO": {"type": project_type, "projectCode": project_code},
                    "baseProjectDetailTO": {
                        "projectCode": project_code,
                        "detailCode": detail_code,
                        "name": detail_name,
                    },
                }
            }
        }
        t1 = time.perf_counter()
        resp = client.engine_execute("WORKTIME$work_hour_filling", body, write=True)
        timings.append({
            "service": "WORKTIME$work_hour_filling",
            "projectCode": project_code,
            "detailCode": detail_code,
            "ms": round((time.perf_counter() - t1) * 1000, 2),
        })
        req_id = resp.get("requestId")
        if req_id:
            request_ids.append(str(req_id))

    verify_result: dict[str, Any] = {}
    if args.verify:
        grouped: dict[tuple[str, str], list[str]] = {}
        for item in cfg:
            key = (str(item["projectType"]), str(item["projectCode"]))
            grouped.setdefault(key, []).append(str(item["detailCode"]))

        for (project_type, project_code), detail_codes in grouped.items():
            t2 = time.perf_counter()
            verify_raw = client.engine_execute(
                "WORKTIME$get_project_detail_work_hours",
                {
                    "params": {
                        "req": {
                            "beginDate": begin_ms,
                            "endDate": end_ms,
                            "baseProjectTO": {
                                "type": project_type,
                                "projectCode": project_code,
                            },
                            "staffs": [{"id": staff_id}],
                        }
                    }
                },
            )
            timings.append({
                "service": "WORKTIME$get_project_detail_work_hours",
                "projectCode": project_code,
                "ms": round((time.perf_counter() - t2) * 1000, 2),
            })
            rows = data_list(verify_raw)
            verify_result[f"{project_type}#{project_code}"] = [
                x for x in rows if str(x.get("detailCode")) in set(detail_codes)
            ]

    # 更新 state（cookie / project_config / 日统计）。
    state.setdefault("auth", {})
    state["auth"]["emp_cookie"] = client.emp_cookie
    state["auth"]["updatedAt"] = now_iso()
    state["project_config"] = cfg
    state.setdefault("stats_cache", {}).setdefault("daily", {})
    state["stats_cache"]["daily"][target_date] = {
        "status": "SUCCESS",
        "details": cfg,
        "ratio": sum(float(i["percentage"]) for i in cfg),
        "lastSuccessAt": now_iso(),
        "sourceRequestId": request_ids[-1] if request_ids else "",
    }
    save_config_state(config_file, state)
    save_stats_cache(records_file, state["stats_cache"])

    result = {
        "date": target_date,
        "staffId": staff_id,
        "filledItems": len(cfg),
        "requestIds": request_ids,
        "verify": verify_result if args.verify else "skipped",
        "timings": timings,
        "configStateFile": str(config_file),
        "recordsStateFile": str(records_file),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def run_verify_day(client: EmpClient, state: dict[str, Any], target_date: str) -> int:
    begin_ms, end_ms = to_day_range_ms(target_date)
    cfg = state.get("project_config") or []
    if not cfg:
        raise RuntimeError("state 中 project_config 为空，无法回查。")

    staff_raw = client.engine_execute("MD$query_current_login_related_employee_info", {"params": {}})
    staff_id = data_obj(staff_raw).get("id")
    if staff_id is None:
        raise RuntimeError("未获取到 staffId。")

    grouped: dict[tuple[str, str], list[str]] = {}
    for item in cfg:
        key = (str(item["projectType"]), str(item["projectCode"]))
        grouped.setdefault(key, []).append(str(item["detailCode"]))

    verify_result: dict[str, Any] = {}
    timings: list[dict[str, Any]] = []
    for (project_type, project_code), detail_codes in grouped.items():
        t0 = time.perf_counter()
        verify_raw = client.engine_execute(
            "WORKTIME$get_project_detail_work_hours",
            {
                "params": {
                    "req": {
                        "beginDate": begin_ms,
                        "endDate": end_ms,
                        "baseProjectTO": {
                            "type": project_type,
                            "projectCode": project_code,
                        },
                        "staffs": [{"id": staff_id}],
                    }
                }
            },
        )
        timings.append({
            "service": "WORKTIME$get_project_detail_work_hours",
            "projectCode": project_code,
            "ms": round((time.perf_counter() - t0) * 1000, 2),
        })
        rows = data_list(verify_raw)
        verify_result[f"{project_type}#{project_code}"] = [
            x for x in rows if str(x.get("detailCode")) in set(detail_codes)
        ]

    print(
        json.dumps(
            {"date": target_date, "staffId": staff_id, "verify": verify_result, "timings": timings},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EMP 工时最小接口脚本（Python）")
    parser.add_argument("--base-url", default=os.getenv("EMP_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--iam-base-url", default=os.getenv("EMP_IAM_BASE_URL", DEFAULT_IAM_BASE_URL))
    parser.add_argument("--iam-referer", default=os.getenv("EMP_IAM_REFERER", DEFAULT_IAM_REFERER))
    parser.add_argument("--cookie", default=os.getenv("EMP_COOKIE", ""))
    parser.add_argument("--iam-cookie", default=os.getenv("EMP_IAM_COOKIE", ""))
    parser.add_argument("--account", default=os.getenv("EMP_ACCOUNT", ""))
    parser.add_argument("--password", default=os.getenv("EMP_PASSWORD", ""))
    parser.add_argument("--password-encrypted", action="store_true", help="--password 已是加密值时开启")
    parser.add_argument("--captcha", default="", help="登录验证码（仅当 prepare 要求时使用）")
    parser.add_argument("--state-file", default="", help="兼容旧参数：等价于 --config-state-file")
    parser.add_argument("--config-state-file", default=str(DEFAULT_CONFIG_STATE_FILE), help="配置缓存文件（auth + project_config）")
    parser.add_argument("--records-state-file", default=str(DEFAULT_RECORDS_STATE_FILE), help="填报记录缓存文件（stats_cache）")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--retries", type=int, default=1)

    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-projects", help="获取项目+子项目清单")
    p_list.add_argument("--date", default=None, help="日期：YYYY-MM-DD（默认 Asia/Shanghai 当天）")
    p_list.add_argument("--force-date", action="store_true", help="允许使用未来/远历史日期")
    p_list.add_argument("--json", action="store_true", help="JSON 输出")

    p_fill = sub.add_parser("fill-day", help="按配置填报某天工时")
    p_fill.add_argument("--date", default=None, help="日期：YYYY-MM-DD（默认 Asia/Shanghai 当天）")
    p_fill.add_argument("--force-date", action="store_true", help="允许使用未来/远历史日期")
    p_fill.add_argument("--config-file", help="project_config JSON 文件路径")
    p_fill.add_argument("--config-json", help="project_config JSON 字符串")
    p_fill.add_argument("--verify", action="store_true", help="写后回查")

    p_verify = sub.add_parser("verify-day", help="按配置缓存中的 project_config 回查某天工时")
    p_verify.add_argument("--date", default=None, help="日期：YYYY-MM-DD（默认 Asia/Shanghai 当天）")
    p_verify.add_argument("--force-date", action="store_true", help="允许使用未来/远历史日期")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.date = resolve_target_date(args.date, getattr(args, "force_date", False))
    except ValueError as exc:
        parser.error(f"日期参数非法：{exc}")
    print(
        f"[date-guard] command={args.command} target_date={args.date} "
        f"force_date={bool(getattr(args, 'force_date', False))}",
        file=sys.stderr,
    )

    config_file_arg = args.state_file or args.config_state_file
    config_file = pathlib.Path(config_file_arg).expanduser().resolve()
    records_file = pathlib.Path(args.records_state_file).expanduser().resolve()

    state = load_config_state(config_file)
    stats_cache = load_stats_cache(records_file)
    # 兼容旧单文件：若 records 为空而 config 中有 stats_cache，则迁移到 records。
    legacy_stats = state.get("stats_cache")
    if isinstance(legacy_stats, dict) and not any(stats_cache.get(k) for k in ("daily", "weekly", "monthly")):
        stats_cache = {
            "daily": legacy_stats.get("daily") or {},
            "weekly": legacy_stats.get("weekly") or {},
            "monthly": legacy_stats.get("monthly") or {},
        }
        save_stats_cache(records_file, stats_cache)
    state["stats_cache"] = stats_cache
    emp_cookie, _, _, _, _, _ = resolve_auth_inputs(args, state)
    if not emp_cookie and not (args.account or args.password or (state.get("auth") or {}).get("account")):
        parser.error("缺少认证信息：请提供 cookie，或提供 account/password 以自动登录。")

    client = EmpClient(
        base_url=args.base_url,
        iam_base_url=args.iam_base_url,
        emp_cookie=emp_cookie,
        iam_cookie=args.iam_cookie,
        iam_referer=args.iam_referer,
        timeout_seconds=args.timeout,
        retries=args.retries,
    )
    try:
        ensure_valid_cookie(client, args, state, config_file)
    except Exception as exc:
        parser.error(f"启动鉴权失败：{exc}")

    if args.command == "list-projects":
        return run_list_projects(client, args.date, as_json=args.json)
    if args.command == "fill-day":
        return run_fill_day(client, state, config_file, records_file, args.date, args)
    if args.command == "verify-day":
        return run_verify_day(client, state, args.date)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("已中断。", file=sys.stderr)
        raise SystemExit(130)
