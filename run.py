import socket
import sys
import uvicorn

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    lan_ip = get_lan_ip()
    port = 8080
    print("\n" + "=" * 55)
    print(">> Server started successfully!")
    print(f"-> Localhost:   http://127.0.0.1:{port}/docs")
    print(f"-> LAN IP:      http://{lan_ip}:{port}/docs")
    print(f"-> Emulator:    http://10.0.2.2:{port}/docs")
    print("=" * 55 + "\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)


