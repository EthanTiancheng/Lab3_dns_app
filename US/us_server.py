from flask import Flask, request, Response
import socket, requests

app = Flask(__name__)

def udp_query(hostname: str, as_ip: str, as_port: int, timeout=2.0):
    msg = f"TYPE=A\nNAME={hostname}\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(msg.encode(), (as_ip, as_port))
        data, _ = sock.recvfrom(2048)
        text = data.decode(errors="ignore")
        if "VALUE=" in text:
            parts = dict(p.split("=", 1) for p in text.splitlines()[1].split() if "=" in p)
            return parts.get("VALUE")
        return None
    finally:
        sock.close()

@app.get("/fibonacci")
def proxy_fibonacci():
    hostname = request.args.get("hostname")
    fs_port  = request.args.get("fs_port")
    number   = request.args.get("number")
    as_ip    = request.args.get("as_ip")
    as_port  = request.args.get("as_port")

    required = {"hostname": hostname, "fs_port": fs_port, "number": number, "as_ip": as_ip, "as_port": as_port}
    if any(v is None or str(v).strip()=="" for v in required.values()):
        return Response("Missing parameter(s)", status=400)

    if not number.isdigit():
        return Response("Bad Request: number must be integer >= 0", status=400)

    try:
        as_port_i = int(as_port)
        fs_port_i = int(fs_port)
    except ValueError:
        return Response("Bad Request: ports must be integers", status=400)

    ip = udp_query(hostname, as_ip, as_port_i)
    if not ip:
        return Response("DNS name not found", status=502)

    url = f"http://{ip}:{fs_port_i}/fibonacci"
    try:
        r = requests.get(url, params={"number": number}, timeout=2.5)
    except requests.RequestException as e:
        return Response(f"FS unreachable: {e}", status=504)

    body = r.text
    if not body.endswith("\n"):
        body += "\n"

    return Response(body, status=r.status_code, content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
