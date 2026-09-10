import requests
import time

BASE_URL = "http://localhost:8000"
API_KEY = "kiemaen-secret-key-2026"
HEADERS = {"X-API-Key": API_KEY}

def run_benchmark():
    print("=== Starting Kiemaen AI Automated Benchmark Suite ===")
    
    # Test 1: Telemetry Health Check
    t0 = time.time()
    res = requests.get(f"{BASE_URL}/api/telemetry", headers=HEADERS)
    dt = time.time() - t0
    assert res.status_code == 200, f"Telemetry failed: {res.status_code}"
    print(f"[PASS] Telemetry Check ({dt:.3f}s) - Active Chunks: {res.json().get('total_rag_chunks')}")

    # Test 2: Ingestion Latency
    sample_doc = "Benchmark Spec Document: Shear capacity limit is 120 kN."
    t0 = time.time()
    files = {"file": ("benchmark.txt", sample_doc.encode('utf-8'))}
    res = requests.post(f"{BASE_URL}/rag/ingest", headers=HEADERS, files=files)
    dt = time.time() - t0
    assert res.status_code == 200, f"Ingestion failed: {res.status_code}"
    print(f"[PASS] RAG Ingestion ({dt:.3f}s)")

    # Test 3: RAG Retrieval Precision
    t0 = time.time()
    payload = {
        "task": "What is the shear capacity limit from the benchmark spec document?",
        "max_iterations": 1
    }
    res = requests.post(f"{BASE_URL}/run_blueprint", headers=HEADERS, json=payload)
    dt = time.time() - t0
    assert res.status_code == 200, f"Blueprint execution failed: {res.status_code}"
    output = res.json().get("final_output", "")
    assert "120" in output, f"RAG Precision test failed. Output: {output}"
    print(f"[PASS] RAG Retrieval Precision ({dt:.3f}s) - Output verified: '120 kN'")

    print("\nAll benchmark tests executed successfully.")

if __name__ == "__main__":
    run_benchmark()
