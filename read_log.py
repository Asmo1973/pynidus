import sys

try:
    with open(sys.argv[1], "r", encoding="utf-16", errors="replace") as f:
        for line in f:
            if any(k in line for k in ["Error", "Fail", "Unicode", "Exception", "E "]):
                print(line.strip())
except Exception as e:
    print(f"Error reading file: {e}")
