import urllib.request
import json

def fetch(url: str):
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            code = resp.getcode()
            body = resp.read().decode('utf-8', errors='ignore')
            return code, body[:500]
    except Exception as e:
        return None, f"ERR: {e}"

def main():
    base = "http://127.0.0.1:8000"
    tests = [
        ("/health", None),
        ("/api/v1/dashboard/stats?subject=python_basics", None),
        ("/api/v1/student/learning-status?subject=python_basics", None),
    ]
    for path, _ in tests:
        code, body = fetch(base + path)
        print(f"{path} -> {code}\n{body}\n")

if __name__ == "__main__":
    main()


