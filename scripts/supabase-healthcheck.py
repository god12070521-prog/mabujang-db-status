#!/usr/bin/env python3
"""Read-only DB heartbeat, with deduplicated GitHub failure/recovery alerts."""
import json
import os
import sys
import time
import urllib.error
import urllib.request


def request_json(url, method="GET", data=None, headers=None):
    request = urllib.request.Request(
        url, data=None if data is None else json.dumps(data).encode(),
        headers={"Content-Type": "application/json", **(headers or {})}, method=method,
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def check_database():
    for attempt in range(3):
        try:
            result = request_json(
                os.environ["SUPABASE_URL"] + "/rest/v1/rpc/vendor_healthcheck",
                method="POST", data={}, headers={"apikey": os.environ["SUPABASE_PUBLISHABLE_KEY"]},
            )
            if result != {"ok": True}:
                raise ValueError("Unexpected DB health response")
            print("Database RPC returned ok=true")
            return True
        except (urllib.error.URLError, ValueError, TimeoutError) as error:
            # Do not print response bodies, headers, credentials, or raw exception text.
            status = error.code if isinstance(error, urllib.error.HTTPError) else type(error).__name__
            print(f"DB check attempt {attempt + 1}/3 failed ({status})")
            if attempt < 2:
                time.sleep(10)
    return False


def notify(healthy):
    repo = os.environ["GITHUB_REPOSITORY"]
    base = f"https://api.github.com/repos/{repo}"
    headers = {"Authorization": "Bearer " + os.environ["GH_TOKEN"],
               "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    test = os.environ.get("NOTIFICATION_TEST") == "true"
    title = ("[알림 시험] " if test else "") + "Supabase DB 상태 확인 실패"
    marker = "<!-- studio-db-healthcheck:" + ("test" if test else "production") + " -->"
    issues = []
    page = 1
    while True:
        batch = request_json(f"{base}/issues?state=open&per_page=100&page={page}", headers=headers)
        issues.extend(i for i in batch if "pull_request" not in i and marker in (i.get("body") or ""))
        if len(batch) < 100:
            break
        page += 1
    run = f"https://github.com/{repo}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    if not healthy and not issues:
        body = (f"{marker}\n\n" + ("실제 장애가 아닌 알림 경로 시험입니다.\n\n" if test else "")
                + "정기 DB 조회가 실패했습니다. Supabase 프로젝트 상태와 GitHub 실행 기록을 확인해 주세요."
                + f"\n\n실행 기록: {run}\n\n다음 조회가 성공하면 복구 댓글을 남기고 자동으로 닫습니다.")
        issue = request_json(f"{base}/issues", "POST",
                             {"title": title, "body": body, "assignees": ["god12070521-prog"]}, headers)
        print("Failure notification issue: " + issue["html_url"])
    elif healthy:
        for issue in issues:
            request_json(f"{base}/issues/{issue['number']}/comments", "POST",
                         {"body": f"DB 조회가 다시 성공했습니다. 복구 확인: {run}"}, headers)
            request_json(f"{base}/issues/{issue['number']}", "PATCH", {"state": "closed"}, headers)
            print("Recovery notification issue: " + issue["html_url"])
    else:
        print("Existing failure issue remains open; duplicate notification suppressed")


if __name__ == "__main__":
    healthy = check_database()
    if os.environ.get("SIMULATE_FAILURE") == "true":
        healthy = False
        print("Notification failure simulation requested")
    if os.environ.get("GH_TOKEN"):
        notify(healthy)
    sys.exit(0 if healthy else 1)
