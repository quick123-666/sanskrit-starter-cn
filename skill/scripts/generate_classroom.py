# -*- coding: utf-8 -*-
"""
Generate an OpenMAIC classroom from a requirement (and optional textbook PDF),
then poll until done and print the classroom URL.

Usage:
  python generate_classroom.py --requirement "为零基础汉语母语者设计梵语入门课程..." [--material "path/to.pdf"] [--voice "温润男声"] [--resume <runId>]

Voice options (MiniMax TTS, id 即中文名):
  --voice "温润男声"   -> Chinese (Mandarin)_Gentleman
  --voice "电台男主播" -> Chinese (Mandarin)_Radio_Host
  --voice "温暖少女"   -> Chinese (Mandarin)_Warm_Girl
  --voice "少女音色"   -> female-shaonv
  --voice "御姐音色"   -> female-yujie (默认)
  --voice "新闻女声"   -> Chinese (Mandarin)_News_Anchor
  --voice "精英青年"   -> male-qn-jingying
省略 --voice 时保持旧行为（headless API，服务端默认音色=御姐音色）；
提供 --voice 时走浏览器同级接口 /api/generation-runs，让新课堂用指定音色配音。

Environment assumptions (see references/openmaic-howto.md):
  - OpenMAIC running at http://localhost:3000 (single-user mode recommended)
  - owner cookie persisted at C:\\OpenMAIC\\_cookie.txt (reused across runs)
"""
import argparse
import json
import time
import uuid
import urllib.request
import urllib.error
import http.cookiejar
import os

BASE = os.environ.get("OPENMAIC_BASE", "http://localhost:3000")
COOKIE = os.environ.get("OPENMAIC_COOKIE", r"C:\OpenMAIC\_cookie.txt")

# MiniMax TTS 中文音色：中文名 -> voiceId
VOICE_IDS = {
    "温润男声": "Chinese (Mandarin)_Gentleman",
    "电台男主播": "Chinese (Mandarin)_Radio_Host",
    "温暖少女": "Chinese (Mandarin)_Warm_Girl",
    "新闻女声": "Chinese (Mandarin)_News_Anchor",
    "少女音色": "female-shaonv",
    "精英青年": "male-qn-jingying",
    "御姐音色": "female-yujie",
}
DEFAULT_VOICE_ID = "female-yujie"

cj = http.cookiejar.MozillaCookieJar(COOKIE)
try:
    cj.load(ignore_discard=True, ignore_expires=True)
except Exception:
    pass
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def save_cookies():
    try:
        cj.save(ignore_discard=True, ignore_expires=True)
    except Exception:
        pass

def req(method, path, body=None, headers=None, timeout=120):
    r = urllib.request.Request(BASE + path, data=body, method=method)
    r.add_header("User-Agent", "openmaic-skill")
    for k, v in (headers or {}).items():
        r.add_header(k, v)
    try:
        resp = opener.open(r, timeout=timeout)
        save_cookies()
        return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        save_cookies()
        return e.code, e.read().decode("utf-8", errors="replace")

def poll_run(rid, interval_ms=5000, cap_sec=3000):
    """Poll the browser-grade run endpoint until a terminal state, return run snapshot."""
    interval = max(interval_ms / 1000.0, 5)
    deadline = time.time() + cap_sec
    last = ""
    while time.time() < deadline:
        st, body = req("GET", f"/api/generation-runs/{rid}")
        if st != 200:
            line = f"poll http={st}"
            if line != last:
                print(line, flush=True)
                last = line
            time.sleep(interval)
            continue
        try:
            run = json.loads(body)["run"]
        except Exception:
            time.sleep(interval)
            continue
        state = run.get("state", "unknown")
        step = run.get("step") or ""
        prog = run.get("progress", {})
        scenes = prog.get("scenesCompleted", 0)
        total = prog.get("scenesTotal", "")
        line = f"state={state} step={step} scenes={scenes}/{total}"
        if line != last:
            print(line, flush=True)
            last = line
        if state in ("completed", "paused", "ended", "cancelled", "failed"):
            return run
        time.sleep(interval)
    return {"state": "timeout"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--requirement", required=True, help="教学要求（中文文本）")
    ap.add_argument("--material", default=None, help="教材 PDF 绝对路径（可选）")
    ap.add_argument("--voice", default=None,
                    help="配音音色中文名（可选）：温润男声/电台男主播/温暖少女/新闻女声/少女音色/精英青年/御姐音色；省略则用服务端默认")
    ap.add_argument("--resume", default=None, help="暂停的 runId（续跑，可选）")
    args = ap.parse_args()

    voice_id = None
    if args.voice:
        voice_id = VOICE_IDS.get(args.voice)
        if not voice_id:
            print(f"UNKNOWN_VOICE {args.voice}（可选：{', '.join(VOICE_IDS)}）", flush=True)
            return 1

    st, _ = req("GET", "/")
    print("WARM", st, flush=True)

    if args.resume:
        rid = args.resume
        payload = json.dumps({"commandId": "retry-" + uuid.uuid4().hex}).encode("utf-8")
        st, body = req("POST", f"/api/generation-runs/{rid}/retry", body=payload,
                       headers={"content-type": "application/json"})
        print("RESUME", st, flush=True)
        if st not in (200, 202):
            print(body[:500], flush=True)
            return 1
        run = json.loads(body).get("run", {})
        run_id = run.get("id") or rid
        result = poll_run(run_id)
    elif voice_id:
        # 浏览器同级接口：带音色偏好，新课堂用指定音色配音
        material_ids = []
        if args.material:
            with open(args.material, "rb") as f:
                data = f.read()
            st, body = req(
                "POST", "/api/materials", body=data,
                headers={"content-type": "application/pdf",
                         "x-material-filename": os.path.basename(args.material)},
                timeout=300)
            print("UPLOAD", st, flush=True)
            if st != 201:
                print(body[:500], flush=True)
                return 1
            mid = json.loads(body)["materialId"]
            print("MATERIAL_ID", mid, flush=True)
            deadline = time.time() + 180
            while time.time() < deadline:
                st, body = req("GET", f"/api/materials/{mid}")
                if st == 200 and "extracting" not in body[:80]:
                    break
                time.sleep(8)
            material_ids = [mid]
        payload = {
            "requirement": args.requirement,
            "interactive": False,
            "taskEngine": False,
            "agents": {"mode": "preset", "agentIds": []},
            "outlineReview": "countdown",
            "voice": {"providerId": "minimax-tts", "voiceId": voice_id, "speed": 1},
        }
        if material_ids:
            payload["materialIds"] = material_ids
            payload["releaseMaterials"] = True
        body = json.dumps(payload).encode("utf-8")
        st, resp_body = req("POST", "/api/generation-runs", body=body,
                            headers={"content-type": "application/json"})
        print("START", st, flush=True)
        if st not in (200, 202):
            print(resp_body[:600], flush=True)
            return 1
        run = json.loads(resp_body).get("run", {})
        run_id = run.get("id")
        if not run_id:
            print("NO_RUN_ID", resp_body[:300], flush=True)
            return 1
        print("RUN_ID", run_id, flush=True)
        print("VOICE", voice_id, flush=True)
        result = poll_run(run_id)
    else:
        # 旧行为：headless API（不带音色偏好）
        material_ids = []
        if args.material:
            with open(args.material, "rb") as f:
                data = f.read()
            st, body = req(
                "POST", "/api/materials", body=data,
                headers={"content-type": "application/pdf",
                         "x-material-filename": os.path.basename(args.material)},
                timeout=300)
            print("UPLOAD", st, flush=True)
            if st != 201:
                print(body[:500], flush=True)
                return 1
            mid = json.loads(body)["materialId"]
            print("MATERIAL_ID", mid, flush=True)
            deadline = time.time() + 180
            while time.time() < deadline:
                st, body = req("GET", f"/api/materials/{mid}")
                if st == 200 and "extracting" not in body[:80]:
                    break
                time.sleep(8)
            material_ids = [mid]
        payload = json.dumps({"requirement": args.requirement,
                              "materialIds": material_ids}).encode("utf-8")
        st, body = req("POST", "/api/generate-classroom", body=payload,
                       headers={"content-type": "application/json"})
        print("START", st, flush=True)
        if st not in (200, 202):
            print(body[:600], flush=True)
            return 1
        j = json.loads(body)
        jid = j.get("jobId") or j.get("runId")
        if not jid:
            print("NO_JOB_ID", body[:300], flush=True)
            return 1
        print("JOB_ID", jid, flush=True)
        result = poll_job(jid)

    if result.get("state") == "completed":
        stage_id = result.get("stageId")
        if stage_id:
            print("CLASSROOM_URL", f"{BASE}/classroom/{stage_id}", flush=True)
            return 0
    print("FINAL", json.dumps(result, ensure_ascii=False)[:1500], flush=True)
    return 1

def poll_job(jid, interval_ms=5000, cap_sec=2400):
    """Legacy headless job poll (unused when --voice is given)."""
    interval = max(interval_ms / 1000.0, 5)
    deadline = time.time() + cap_sec
    last = ""
    while time.time() < deadline:
        st, body = req("GET", f"/api/generate-classroom/{jid}")
        try:
            j = json.loads(body)
        except Exception:
            j = {}
        status = j.get("status", "unknown")
        progress = j.get("progress", 0)
        step = j.get("step", "")
        line = f"status={status} step={step} progress={progress}"
        if line != last:
            print(line, flush=True)
            last = line
        if status in ("succeeded", "failed", "cancelled", "error"):
            return j
        time.sleep(interval)
    return {"status": "timeout"}

if __name__ == "__main__":
    raise SystemExit(main())
