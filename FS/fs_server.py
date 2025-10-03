from flask import Flask, request, Response
import socket

app = Flask(__name__)

def send_udp(msg: str, ip: str, port: int, timeout=2.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(msg.encode(), (ip, port))
        data, _ = sock.recvfrom(2048)  
        return data.decode(errors="ignore")
    finally:
        sock.close()

def fib(n: int) -> int:
    if n < 0: 
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+b
    return a

@app.put("/register")
def register():
    try:
        body = request.get_json(force=True)
    except Exception:
        return Response("Bad JSON", status=400)

    for k in ("hostname", "ip", "as_ip", "as_port"):
        if k not in body or not body[k]:
            return Response(f"Missing {k}", status=400)

    hostname = str(body["hostname"]).strip()
    fs_ip    = str(body["ip"]).strip()
    as_ip    = str(body["as_ip"]).strip()
    as_port  = int(body["as_port"])

    msg = f"TYPE=A\nNAME={hostname} VALUE={fs_ip} TTL=10\n"
    try:
        _ = send_udp(msg, as_ip, as_port)
    except Exception as e:
        return Response(f"AS not reachable: {e}", status=400)

    return Response("Registered\n", status=201, mimetype="text/plain")
    
@app.get("/fibonacci")
def fibonacci():
    x = request.args.get("number")
    if x is None or not x.isdigit():
        return Response("Bad Request: number must be integer >= 0", status=400)
    val = fib(int(x))
    return str(val), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
