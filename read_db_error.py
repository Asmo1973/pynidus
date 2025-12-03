try:
    with open("warnings.log", "r", encoding="utf-16", errors="replace") as f:
        for line in f:
            if "Warning" in line or "warning" in line:
                print(line.strip())
except Exception as e:
    print(f"Error: {e}")
