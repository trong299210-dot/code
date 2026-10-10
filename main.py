import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import bot

# Web server siêu nhẹ bằng thư viện chuẩn của Python (không cần cài thêm flask)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Discord Quiz Bot Server</title>
            <style>
                body { font-family: Arial, sans-serif; background: #0f172a; color: white; text-align: center; padding-top: 50px; }
                .card { background: #1e293b; display: inline-block; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
                .status { color: #22c55e; font-weight: bold; font-size: 20px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🤖 Discord Python Quiz Bot</h1>
                <p class="status">● Status: ONLINE 24/7</p>
                <p>Website nay giu cho Bot Discord hoat dong lien tuc tren Cloud!</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        # Tắt log http để không rác console
        pass

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Web server dang chay tai port {port}")
    server.serve_forever()

if __name__ == "__main__":
    # 1. Chạy Web Server ở luồng ngầm (Background Thread)
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # 2. Chạy Discord Bot ở luồng chính
    token = bot.TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("Error: Missing DISCORD_BOT_TOKEN")
    else:
        bot.bot.run(token)
