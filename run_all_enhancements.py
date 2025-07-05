import requests
import time

API = "http://localhost:5005/api"
SECRET = "N8NSuperSecret"

def run_cycle():
    r = requests.post(f"{API}/trigger-enhancement-cycle", headers={"x-mcp-secret": SECRET})
    print(r.json())

def check_remaining():
    r = requests.get(f"{API}/enhancements", headers={"x-mcp-secret": SECRET})
    return [e for e in r.json() if e["status"] == "new"]

if __name__ == "__main__":
    while True:
        outstanding = check_remaining()
        if not outstanding:
            print("No enhancements left to process.")
            break
        print(f"Processing {len(outstanding)} enhancement(s)...")
        run_cycle()
        time.sleep(10)  # Give your agent time to finish each cycle
