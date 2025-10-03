import socket, os

HOST = "0.0.0.0"
PORT = 53533
DB_FILE = "dns_records.txt"  # 简单持久化，文本文件

def load_db():
    db = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line: 
                    continue
                try:
                    name, value, ttl = line.split()
                    db[name] = (value, int(ttl))
                except:
                    pass
    return db

def save_db(db):
    with open(DB_FILE, "w") as f:
        for name, (value, ttl) in db.items():
            f.write(f"{name} {value} {ttl}\n")

def parse_msg(data: bytes):
    text = data.decode("utf-8", errors="ignore").strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines: 
        return None
    if not lines[0].startswith("TYPE="):
        return None
    # 注册：两行里第二行包含 VALUE 和 TTL
    if len(lines) >= 2 and ("VALUE=" in lines[1] and "TTL=" in lines[1]):
        fields = dict(item.split("=", 1) for item in lines[1].split() if "=" in item)
        return ("register", fields.get("NAME"), fields.get("VALUE"), int(fields.get("TTL", "10")))
    # 查询：两行里第二行只有 NAME=
    if len(lines) >= 2 and lines[1].startswith("NAME="):
        return ("query", lines[1].split("=", 1)[1], None, None)
    return None

def main():
    db = load_db()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[AS] listening UDP {HOST}:{PORT}")

    while True:
        data, addr = sock.recvfrom(2048)
        parsed = parse_msg(data)
        if not parsed:
            continue
        mode, name, value, ttl = parsed

        if mode == "register" and name and value:
            db[name] = (value, ttl or 10)
            save_db(db)
            resp = f"TYPE=A\nNAME={name} VALUE={value} TTL={db[name][1]}\n"
            sock.sendto(resp.encode(), addr)
            print(f"[AS] Registered {name} -> {value} ttl={db[name][1]}")
        elif mode == "query" and name:
            if name in db:
                val, t = db[name]
                resp = f"TYPE=A\nNAME={name} VALUE={val} TTL={t}\n"
            else:
                resp = f"TYPE=A\nNAME={name}\n"
            sock.sendto(resp.encode(), addr)
            print(f"[AS] Query {name} -> {resp.strip()}")

if __name__ == "__main__":
    main()
