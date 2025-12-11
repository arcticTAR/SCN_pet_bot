from flask import Flask, request, jsonify

app = Flask(__name__)

# Тестовый маршрут — чтобы проверить, что backend работает
@app.route("/", methods=["GET"])
def home():
    return "Backend is alive!", 200


# Маршрут под webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("Получены данные:", data)  # лог в Render → Logs

    # Просто возвращаем OK чтобы бот видел, что всё дошло
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
