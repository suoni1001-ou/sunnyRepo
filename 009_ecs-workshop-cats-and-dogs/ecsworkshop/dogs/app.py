import os
from html import escape

import pymysql
from flask import Flask, render_template_string, request

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def get_conn():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

@app.route("/dogs")
def dogs():
    client_ip = request.remote_addr
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS dog_visits (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        path VARCHAR(255) NOT NULL,
                        client_ip VARCHAR(45),
                        visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cur.execute(
                    "INSERT INTO dog_visits (path, client_ip) VALUES (%s, %s)",
                    ("/dogs", client_ip)
                )
                cur.execute("SELECT COUNT(*) AS cnt FROM dog_visits")
                count = cur.fetchone()["cnt"]
        status = "Aurora 接続成功"
    except Exception as e:
        count = "取得できません"
        status = "Aurora 接続エラー"
        print("DB ERROR:", e)

    html = f"""
    <html>
      <body style="font-family:Arial; text-align:center; padding:30px;">
        <h1>Dogs</h1>
        <p>{escape(status)}</p>
        <p>/dogs のアクセスで Aurora の dog_visits に 1 行追加しました。</p>
        <p>トータル件数: <strong>{escape(str(count))}</strong></p>
      </body>
    </html>
    """
    return render_template_string(html)

@app.route("/health")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)