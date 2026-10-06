#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare KV User Statistics Monitor for Psychology 347 Quiz System
- Queries Cloudflare Workers KV (PSYCH_KV)
- Displays registered users, learning progress, accuracy, and active timestamps
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import urllib.error
import ssl

# Configure robust SSL context to handle macOS python certificate stores
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = ssl._create_unverified_context()

# If certifi is present but system store still fails, ensure fallback
if not hasattr(SSL_CTX, 'check_hostname') or SSL_CTX.verify_mode != ssl.CERT_NONE:
    try:
        urllib.request.urlopen("https://1.1.1.1", context=SSL_CTX, timeout=2)
    except Exception:
        SSL_CTX = ssl._create_unverified_context()

# Cloudflare Configuration
DEFAULT_ACCOUNT_ID = "697914996ff10a8db042bceddf4fb126"
DEFAULT_KV_NAMESPACE_ID = "cb742ba3265946039f62c39b38e72206"
DEFAULT_TOKEN_FILE = "/Volumes/Ext/dev/CF/cf_api_token"
TOTAL_BANK_QUESTIONS = 254


def get_cf_token(token_file: str = DEFAULT_TOKEN_FILE) -> str:
    """Retrieve Cloudflare API Token from environment or credential file."""
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token and os.path.exists(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            token = f.read().strip()
    if not token:
        print("[!] Error: Cloudflare API Token not found in environment or", token_file)
        sys.exit(1)
    return token


def make_cf_request(url: str, token: str) -> dict:
    """Send an authenticated GET request to Cloudflare API."""
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "PsychQuizStats/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw": content}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        return {"error": f"HTTP {e.code}: {err_msg}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_all_user_keys(account_id: str, namespace_id: str, token: str) -> list:
    """Fetch all keys starting with 'user:' from Cloudflare KV."""
    keys = []
    cursor = ""
    while True:
        url = (
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/"
            f"storage/kv/namespaces/{namespace_id}/keys?prefix=user:&limit=1000"
        )
        if cursor:
            url += f"&cursor={cursor}"

        res = make_cf_request(url, token)
        if not res.get("success"):
            print("[!] Failed to list KV keys:", res.get("errors") or res.get("error"))
            break

        result = res.get("result", [])
        keys.extend(result)

        cursor = res.get("result_info", {}).get("cursor", "")
        if not cursor:
            break

    return keys


def fetch_single_user_record(key_name: str, account_id: str, namespace_id: str, token: str) -> dict:
    """Fetch and parse a single user's record from KV."""
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/"
        f"storage/kv/namespaces/{namespace_id}/values/{key_name}"
    )
    raw = make_cf_request(url, token)

    if isinstance(raw, dict) and "error" in raw:
        return {"key": key_name, "error": raw["error"]}

    # raw might be dict or json parsed
    data = raw if isinstance(raw, dict) else {}
    if "raw" in raw:
        try:
            data = json.loads(raw["raw"])
        except Exception:
            data = {}

    username = data.get("username") or key_name.replace("user:", "")
    auth_code = data.get("authCode", "无")
    updated_at_ms = data.get("updatedAt", 0)

    # Format datetime
    if updated_at_ms:
        try:
            last_sync_str = datetime.fromtimestamp(updated_at_ms / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            last_sync_str = str(updated_at_ms)
    else:
        last_sync_str = "从未"

    payload = data.get("payload", {})
    answers = payload.get("answers", {})
    stars = payload.get("stars", [])
    wrongs = payload.get("wrongs", [])
    mastered = payload.get("mastered", [])

    total_answered = len(answers)
    correct_count = 0
    for ans in answers.values():
        if isinstance(ans, dict) and ans.get("isCorrect"):
            correct_count += 1

    accuracy = (correct_count / total_answered * 100.0) if total_answered > 0 else 0.0

    return {
        "username": username,
        "authCode": auth_code,
        "updatedAtMs": updated_at_ms,
        "lastSyncTime": last_sync_str,
        "totalAnswered": total_answered,
        "correctCount": correct_count,
        "accuracy": accuracy,
        "wrongCount": len(wrongs),
        "starCount": len(stars),
        "masteredCount": len(mastered),
    }


def main():
    parser = argparse.ArgumentParser(description="心理学导论 347 题库系统 · 用户统计与学习进度监控")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出原始数据")
    parser.add_argument("--csv", action="store_true", help="以 CSV 格式输出表格")
    parser.add_argument("-w", "--workers", type=int, default=8, help="并行请求并发线程数 (默认: 8)")
    args = parser.parse_args()

    token = get_cf_token()
    account_id = DEFAULT_ACCOUNT_ID
    namespace_id = DEFAULT_KV_NAMESPACE_ID

    print("[*] 正在连接 Cloudflare Workers KV 检索用户档案...")
    t0 = time.time()
    user_keys = fetch_all_user_keys(account_id, namespace_id, token)

    if not user_keys:
        print("[-] 当前暂无已注册/已同步的云端用户。")
        sys.exit(0)

    print(f"[+] 发现 {len(user_keys)} 位云端注册用户，正在并发抓取详细学习进度...")

    # Parallel fetch user values
    user_records = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(fetch_single_user_record, k.get("name", ""), account_id, namespace_id, token)
            for k in user_keys
        ]
        for f in futures:
            res = f.result()
            if res and "username" in res:
                user_records.append(res)

    duration = time.time() - t0

    # Sort users by last update timestamp (newest first)
    user_records.sort(key=lambda x: x["updatedAtMs"], reverse=True)

    # Calculate Aggregated Metrics
    total_users = len(user_records)
    now_ms = time.time() * 1000
    ms_24h = 24 * 3600 * 1000
    ms_7d = 7 * 24 * 3600 * 1000

    active_24h = sum(1 for u in user_records if (now_ms - u["updatedAtMs"]) <= ms_24h)
    active_7d = sum(1 for u in user_records if (now_ms - u["updatedAtMs"]) <= ms_7d)
    total_questions_done = sum(u["totalAnswered"] for u in user_records)
    total_wrongs_accum = sum(u["wrongCount"] for u in user_records)
    avg_accuracy = (
        sum(u["accuracy"] for u in user_records if u["totalAnswered"] > 0)
        / max(1, sum(1 for u in user_records if u["totalAnswered"] > 0))
    )

    if args.json:
        output_payload = {
            "summary": {
                "totalUsers": total_users,
                "activeLast24h": active_24h,
                "activeLast7d": active_7d,
                "totalQuestionsAnswered": total_questions_done,
                "averageAccuracy": round(avg_accuracy, 1),
                "queryDurationSeconds": round(duration, 2),
            },
            "users": user_records,
        }
        print(json.dumps(output_payload, ensure_ascii=False, indent=2))
        return

    if args.csv:
        print("序号,用户名,授权认证码,已做题数,做题进度(%),正确题数,正确率(%),错题数,收藏数,最后同步时间")
        for idx, u in enumerate(user_records, start=1):
            progress_pct = round((u["totalAnswered"] / TOTAL_BANK_QUESTIONS) * 100, 1)
            print(
                f"{idx},{u['username']},{u['authCode']},{u['totalAnswered']},{progress_pct}%,"
                f"{u['correctCount']},{u['accuracy']:.1f}%,{u['wrongCount']},{u['starCount']},{u['lastSyncTime']}"
            )
        return

    # Print Terminal Dashboard
    print("\n" + "=" * 78)
    print(" 📊 心理学导论 347 · 云端用户量与学习进度实时看板")
    print("=" * 78)
    print(f" 👥 总注册用户数:     {total_users:<6} 位          ⚡ 抓取耗时: {duration:.2f} 秒")
    print(f" 🟢 24小时内活跃:     {active_24h:<6} 位          📅 7日内活跃: {active_7d} 位")
    print(f" 📝 全网累计答题:     {total_questions_done:<6} 次          🎯 平均正确率: {avg_accuracy:.1f}%")
    print(f" 📚 题库总题目数:     {TOTAL_BANK_QUESTIONS:<6} 道          ❌ 累计错题数: {total_wrongs_accum} 道")
    print("=" * 78)

    print(
        f"{'序号':<4} {'用户名':<16} {'授权码':<16} {'做题量':<10} {'正确率':<8} {'错题':<6} {'收藏':<6} {'最近同步时间':<19}"
    )
    print("-" * 78)

    for idx, u in enumerate(user_records, start=1):
        progress_str = f"{u['totalAnswered']}/{TOTAL_BANK_QUESTIONS}"
        acc_str = f"{u['accuracy']:.1f}%" if u["totalAnswered"] > 0 else "-"
        print(
            f"{idx:<4} {u['username'][:15]:<16} {u['authCode'][:15]:<16} "
            f"{progress_str:<10} {acc_str:<8} {u['wrongCount']:<6} {u['starCount']:<6} {u['lastSyncTime']:<19}"
        )

    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
