try:
    with open("zmq_inproc_debug.log", "r", encoding="utf-16", errors="replace") as f:
        for line in f:
            print(line.strip())
except Exception as e:
    print(f"Error: {e}")
