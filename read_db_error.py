try:
    with open("idempotency_error_2.log", "r", encoding="utf-16", errors="replace") as f:
        for line in f:
            if any(k in line for k in ["Error", "Fail", "Exception"]):
                print(line.strip())
except Exception as e:
    print(f"Error: {e}")
