import os

for root, dirs, files in os.walk("."):
    if "migrations" in root:
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "rb") as f:
                    if b"\x00" in f.read():
                        print(f"Null byte found in: {path}")

