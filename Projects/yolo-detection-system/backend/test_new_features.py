# -*- coding: utf-8 -*-
"""新功能全链路测试：模型对比 / 样本池 / PDF 报告 / AI 问答带上下文。

运行前提：后端已启动（http://localhost:5000），存在账号 admin/password123 与至少一条历史记录。
运行方式：python backend/test_new_features.py
"""
import io
import zipfile

import requests

BASE_URL = "http://localhost:5000/api"
USERNAME = "admin"
PASSWORD = "password123"

PASSED = []
FAILED = []


def check(name, condition, detail=""):
    if condition:
        PASSED.append(name)
        print(f"[PASS] {name}")
    else:
        FAILED.append(name)
        print(f"[FAIL] {name} {detail}")


def login():
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": USERNAME, "password": PASSWORD
    }, timeout=10)
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_model_compare(headers):
    resp = requests.get(f"{BASE_URL}/admin/stats/model-compare", headers=headers, timeout=10)
    data = resp.json().get("data", {})
    versions = data.get("versions", [])
    check("model-compare 返回 200", resp.status_code == 200)
    check("model-compare 含版本列表", len(versions) > 0, f"versions={len(versions)}")
    if versions:
        first = versions[0]
        required = ("model_version", "total", "disease_count", "healthy_count",
                    "avg_confidence", "class_distribution")
        missing = [k for k in required if k not in first]
        check("model-compare 字段完整", not missing, f"missing={missing}")


def test_sample_pool_flow(headers):
    # 找一条当前用户的历史记录
    resp = requests.get(f"{BASE_URL}/history", params={"page": 1, "page_size": 1},
                        headers=headers, timeout=10)
    items = resp.json().get("data", {}).get("list", [])
    check("history 列表有数据", len(items) > 0)
    if not items:
        return None
    history_id = items[0]["id"]

    # 已提交过则直接返回（防重复）
    exists = requests.get(f"{BASE_URL}/sample-pool", headers=headers, timeout=10)
    if any(r["history_id"] == history_id for r in exists.json().get("data", {}).get("list", [])):
        check("sample-pool 防重复（已存在记录）", True)
        return history_id

    resp = requests.post(f"{BASE_URL}/sample-pool", headers=headers, json={
        "history_id": history_id,
        "mark_type": "misclassified",
        "corrected_class": "早疫病",
        "note": "测试反馈"
    }, timeout=10)
    check("sample-pool 提交成功", resp.status_code == 200, resp.text[:120])

    # 防重复校验
    resp2 = requests.post(f"{BASE_URL}/sample-pool", headers=headers, json={
        "history_id": history_id, "mark_type": "correct"
    }, timeout=10)
    check("sample-pool 防重复返回 400", resp2.status_code == 400, resp2.text[:120])
    return history_id


def test_admin_sample_pool(headers, history_id):
    resp = requests.get(f"{BASE_URL}/admin/sample-pool", params={"status": "pending"},
                        headers=headers, timeout=10)
    data = resp.json().get("data", {})
    check("admin sample-pool 列表", resp.status_code == 200 and "list" in data)
    check("admin sample-pool stats", isinstance(data.get("stats"), dict))

    target = next((r for r in data.get("list", []) if r.get("history_id") == history_id), None)
    if target:
        resp = requests.put(
            f"{BASE_URL}/admin/sample-pool/{target['id']}/review", headers=headers,
            json={"status": "approved", "review_note": "测试通过"}, timeout=10)
        check("admin sample-pool 审核", resp.status_code == 200, resp.text[:120])

    resp = requests.get(f"{BASE_URL}/admin/sample-pool/export", headers=headers, timeout=30)
    is_zip = resp.content[:2] == b"PK"
    check("admin sample-pool 导出 zip", resp.status_code == 200 and is_zip,
          f"magic={resp.content[:2]}")
    if is_zip:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            names = zf.namelist()
            check("zip 含 README 与 metadata", any("README" in n for n in names)
                  and any("metadata" in n for n in names), f"names={names[:5]}")


def test_history_pdf(headers):
    resp = requests.get(f"{BASE_URL}/history", params={"page": 1, "page_size": 1},
                        headers=headers, timeout=10)
    items = resp.json().get("data", {}).get("list", [])
    if not items:
        check("history PDF（无记录跳过）", True)
        return
    history_id = items[0]["id"]
    resp = requests.get(f"{BASE_URL}/history/{history_id}/report/pdf", headers=headers, timeout=30)
    check("history PDF 返回 200", resp.status_code == 200)
    check("history PDF 魔数 %PDF", resp.content[:4] == b"%PDF", f"magic={resp.content[:4]}")


def test_ask_with_context(headers):
    resp = requests.post(f"{BASE_URL}/knowledge/ask", headers=headers, json={
        "question": "早疫病怎么防治？",
        "detection_context": "早疫病 (95.0%)",
        "detected_class_id": 1
    }, timeout=60)
    data = resp.json().get("data") or {}
    answer = data.get("answer") or ""
    # LLM 外部服务不可用时后端仍应返回 200（mock 或错误兜底）
    check("ask 带上下文返回 200", resp.status_code == 200)
    check("ask 带上下文返回回答", len(answer) > 10, f"answer_len={len(answer)} resp={resp.text[:120]}")


def main():
    headers = login()
    print("登录成功\n")
    history_id = test_sample_pool_flow(headers)
    test_model_compare(headers)
    if history_id:
        test_admin_sample_pool(headers, history_id)
    test_history_pdf(headers)
    test_ask_with_context(headers)

    print(f"\n结果: {len(PASSED)} passed, {len(FAILED)} failed")
    if FAILED:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
