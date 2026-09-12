"""
Automated Test Suite for Multi-Agent Worker-Reviewer System
"""

import time
import json
import httpx
from typing import Dict, Any

API_URL = "http://localhost:8000/run-agent"
HEALTH_URL = "http://localhost:8000/"

# Test scenarios covering different tasks and iteration parameters
TEST_SUITES = [
    {
        "name": "Scenario 1: Python Algorithm Construction",
        "payload": {
            "task": "Write a Python function to check if a string is a palindrome ignoring case and non-alphanumeric characters.",
            "max_iterations": 3,
        },
    },
    {
        "name": "Scenario 2: Data Structure & Complexity Optimization",
        "payload": {
            "task": "Write an efficient Python function to find two numbers in an array that sum up to a target value (Two Sum problem). Provide O(n) time complexity.",
            "max_iterations": 2,
        },
    },
    {
        "name": "Scenario 3: System Architecture / FastAPI Spec",
        "payload": {
            "task": "Write a FastAPI endpoint with pydantic request validation for a user registration endpoint.",
            "max_iterations": 3,
        },
    },
]


def check_health() -> bool:
    """Verifies that the FastAPI backend server is online before running tests."""
    try:
        response = httpx.get(HEALTH_URL, timeout=5.0)
        return response.status_code == 200 and response.json().get("status") == "online"
    except Exception:
        return False


def print_banner(title: str, char: str = "="):
    line = char * 70
    print(f"\n{line}\n {title}\n{line}")


def run_test(scenario: Dict[str, Any], index: int) -> Dict[str, Any]:
    name = scenario["name"]
    payload = scenario["payload"]

    print_banner(f"TEST {index + 1}: {name}")
    print(f"  Task Prompt    : {payload['task']}")
    print(f"  Max Iterations : {payload['max_iterations']}")
    print("  Status         : Sending request to agent system...")

    start_time = time.time()
    try:
        with httpx.Client(timeout=120.0) as client:
            res = client.post(API_URL, json=payload)
            elapsed = time.time() - start_time

            if res.status_code == 200:
                data = res.json()
                print(f"  Result Status  : {data.get('status')}")
                print(f"  Iterations Used: {data.get('iterations_used')}")
                print(f"  Execution Time : {elapsed:.2f} seconds")
                print("  Review Feedback:")
                print(f"    {data.get('review_feedback')}")
                print("-" * 70)
                print("  Final Worker Solution Output:")
                solution_lines = data.get("final_output", "").splitlines()
                for line in solution_lines[:15]:  # Preview first 15 lines
                    print(f"    {line}")
                if len(solution_lines) > 15:
                    print("    ... [truncated for brevity]")

                return {
                    "name": name,
                    "passed": True,
                    "status": data.get("status"),
                    "iterations": data.get("iterations_used"),
                    "time": round(elapsed, 2),
                }
            else:
                print(f"  FAILED: HTTP {res.status_code} - {res.text}")
                return {
                    "name": name,
                    "passed": False,
                    "error": f"HTTP {res.status_code}",
                    "time": round(elapsed, 2),
                }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ERROR: Exception occurred - {str(e)}")
        return {
            "name": name,
            "passed": False,
            "error": str(e),
            "time": round(elapsed, 2),
        }


def main():
    print_banner("MULTI-AGENT WORKER-REVIEWER AUTOMATED TEST SUITE", "#")
    print("Checking backend server health...")

    if not check_health():
        print(
            " [ERROR] Backend FastAPI server is not reachable at http://localhost:8000/"
        )
        print("         Please start the server first in another Termux session using:")
        print("         uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return

    print(" [OK] Backend server is online and operational.\n")

    summary = []
    for idx, test in enumerate(TEST_SUITES):
        result = run_test(test, idx)
        summary.append(result)
        time.sleep(1)

    # Print Summary Report Table
    print_banner("SUMMARY TEST REPORT", "#")
    print(
        f"{'No.':<4} | {'Scenario Name':<42} | {'Status':<10} | {'Iters':<6} | {'Time (s)':<8}"
    )
    print("-" * 78)

    passed_count = 0
    for idx, res in enumerate(summary, 1):
        status_str = "PASS" if res["passed"] else "FAIL"
        if res["passed"]:
            passed_count += 1
        iters_str = str(res.get("iterations", "N/A"))
        time_str = f"{res.get('time', 0.0):.2f}"
        print(
            f"{idx:<4} | {res['name']:<42} | {status_str:<10} | {iters_str:<6} | {time_str:<8}"
        )

    print("-" * 78)
    print(
        f"Total Tests Executed: {len(TEST_SUITES)} | Passed: {passed_count} | Failed: {len(TEST_SUITES) - passed_count}"
    )
    print("#" * 78)


if __name__ == "__main__":
    main()
