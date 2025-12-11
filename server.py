from flask import Flask, request, jsonify
from db import init_db, get_connection

app = Flask(__name__)

# ИНИЦИАЛИЗАЦИЯ БД при запуске приложения
init_db()


@app.route("/", methods=["GET"])
def home():
    return "Backend with DB is alive!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Обязательно проверим вход
    required = ["date", "time", "master", "client", "service"]
    if not all(k in data and data[k] for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    # Запись в БД
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO schedule (date, time, master, client, service, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["date"],
        data["time"],
        data["master"],
        data["client"],
        data["service"],
        data.get("phone")
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "saved"}), 200


@app.route("/get_schedule", methods=["GET"])
def get_schedule():
    """Пример: получить все записи расписания"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM schedule ORDER BY date, time")
    rows = [dict(row) for row in cur.fetchall()]

    conn.close()
    return jsonify(rows), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
