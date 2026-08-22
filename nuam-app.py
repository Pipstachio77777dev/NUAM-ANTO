import threading
import webbrowser

from flask import Flask

app = Flask(__name__)

PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NUAM-ANTO</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0;
               display: flex; flex-direction: column; align-items: center; justify-content: center;
               min-height: 100vh; margin: 0; }
        h1 { color: #38bdf8; margin-bottom: 8px; }
        p { color: #94a3b8; }
        .card { background: #1e293b; padding: 40px 60px; border-radius: 16px;
                box-shadow: 0 10px 30px rgba(0,0,0,.4); text-align: center; }
    </style>
</head>
<body>
    <div class="card">
        <h1>NUAM-ANTO</h1>
        <p>Servidor funcionando correctamente en <b>http://127.0.0.1:5000</b></p>
    </div>
</body>
</html>"""


@app.route("/")
def index():
    return PAGE


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
