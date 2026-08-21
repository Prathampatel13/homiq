import json
import os

with open("full_spectrum_test_report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["results"]
summary = data["summary"]
categories = data["category_breakdown"]

out_path = r"C:\Users\prath\.gemini\antigravity-cli\brain\f3a79a13-44ae-48f7-ad18-7dc6dec49dd3\backend_endpoint_audit_table.md"

lines = []
lines.append("# HomiQ Backend - Complete Endpoint & API Audit Matrix")
lines.append("")
ts = summary["timestamp"]
tot = summary["total_tests"]
pass_cnt = summary["passed"]
fail_cnt = summary["failed"]
pr = summary["pass_rate_percent"]
dur = summary["duration_seconds"]

lines.append(f"**Execution Timestamp**: `{ts}`  ")
lines.append(f"**Total Executed**: `{tot}` | **Passed**: `{pass_cnt}` | **Failed**: `{fail_cnt}` | **Pass Rate**: `{pr}%` | **Duration**: `{dur}s`  ")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 1. Category Summary")
lines.append("")
lines.append("| Test Category | Total | Passed | Failed | Success Rate |")
lines.append("| :--- | :---: | :---: | :---: | :---: |")
for cat, stats in sorted(categories.items()):
    c_tot = stats["total"]
    c_pass = stats["passed"]
    c_fail = stats["failed"]
    p_rate = round((c_pass / c_tot) * 100, 1) if c_tot else 0
    lines.append(f"| **{cat}** | {c_tot} | {c_pass} | {c_fail} | {p_rate}% |")

lines.append("")
lines.append("---")
lines.append("")
lines.append("## 2. Complete Endpoint Audit Table")
lines.append("")
lines.append("| # | Test ID | Method | Endpoint | Actor | Request Data | Expected | Actual | Failure Reason | Code Changed | Result |")
lines.append("| :--- | :--- | :---: | :--- | :---: | :--- | :---: | :---: | :--- | :--- | :---: |")

for idx, r in enumerate(results, start=1):
    test_id = r["test_id"]
    method = r["method"]
    path = r["path"]
    actor = r["actor"]
    req = r["request_summary"].replace("|", "\\|").replace("\n", " ")
    expected = ", ".join(map(str, r["expected_status"]))
    actual = str(r["actual_status"])
    err = (r["error_detail"] or "None").replace("|", "\\|").replace("\n", " ")[:80]
    code = (r["code_changed"] or "None").replace("|", "\\|").replace("\n", " ")
    status = "✅ PASS" if r["passed"] else "❌ FAIL"
    lines.append(f"| {idx} | `{test_id}` | `{method}` | `{path}` | `{actor}` | `{req}` | `{expected}` | `{actual}` | {err} | {code} | {status} |")

lines.append("")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Successfully generated audit table at: {out_path}")
