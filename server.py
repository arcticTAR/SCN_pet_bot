from flask import Flask, request, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__)
DB = "database.db"

# Создание таблиц при старте
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            master TEXT NOT NULL,
            client TEXT,
            service TEXT,
            phone TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS incoming (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            master TEXT,
            client TEXT,
            service TEXT,
            phone TEXT,
            created_at TEXT
        );
    """)

    conn.commit()
    conn.close()


# Проверка занятости слота
def is_slot_busy(date, time, master):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT client FROM schedule
        WHERE date = ? AND time = ? AND master = ?
    """, (date, time, master))

    result = cur.fetchone()
    conn.close()

    return result and result[0] is not None


# Создание записи
def create_record(date, time, master, client, service, phone):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        UPDATE schedule
        SET client = ?, service = ?, phone = ?
        WHERE date = ? AND time = ? AND master = ?
    """, (client, service, phone, date, time, master))

    # если строки нет — создаём
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO schedule (date, time, master, client, service, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, time, master, client, service, phone))

    conn.commit()
    conn.close()


@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    date = data.get("date")
    time = data.get("time")
    master = data.get("master")
    client = data.get("client")
    service = data.get("service")
    phone = data.get("phone")

    # Логирование входящих
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO incoming (date, time, master, client, service, phone, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (date, time, master, client, service, phone, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

    # Проверяем слот
    if is_slot_busy(date, time, master):
        return jsonify({"status": "busy", "message": "Время занято"}), 200

    # Создаем запись
    create_record(date, time, master, client, service, phone)

    return jsonify({"status": "ok", "message": "Запись успешно создана"}), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

