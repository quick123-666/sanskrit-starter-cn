# -*- coding: utf-8 -*-
"""
Check OpenMAIC service and its PostgreSQL dependency.

Usage:
  python health_check.py            # check + human-readable report
  python health_check.py --json     # machine-readable

Exits 0 when everything is healthy, 1 otherwise.
"""
import argparse
import json
import os
import subprocess
import urllib.request

BASE = "http://localhost:3000"
PG_SERVICE = "postgresql-x64-16"
PROJECT_DIR = r"C:\OpenMAIC"

def http_json(path, timeout=15):
    try:
        r = urllib.request.urlopen(BASE + path, timeout=timeout)
        return r.status, json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {e}"}

def pg_service_state():
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-Service {PG_SERVICE} | Select-Object -ExpandProperty Status"],
            capture_output=True, text=True, timeout=30)
        return out.stdout.strip() or out.stderr.strip() or "unknown"
    except Exception as e:
        return f"error: {e}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    st, health = http_json("/api/health")
    _, providers = http_json("/api/server-providers")
    pg = pg_service_state()
    dev_on = os.path.exists(os.path.join(PROJECT_DIR, ".next", "dev"))

    report = {
        "service": "ok" if st == 200 and health.get("status") == "ok" else "down",
        "http": st,
        "version": health.get("version"),
        "pg_service": pg,
        "minimax_models": (providers.get("providers", {}).get("minimax", {})
                           if isinstance(providers, dict) else None),
        "project_dir": PROJECT_DIR,
        "dev_build_present": dev_on,
        "hint": None,
    }
    if report["service"] != "ok":
        report["hint"] = (
            f"OpenMAIC 未运行。检查 PostgreSQL 服务（{PG_SERVICE}）为 Running，"
            f"然后在 {PROJECT_DIR} 执行 pnpm dev，等 30–60 秒后重试。"
        )
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        for k, v in report.items():
            if v is not None:
                print(f"{k}: {v}")
    return 0 if report["service"] == "ok" else 1

if __name__ == "__main__":
    raise SystemExit(main())
