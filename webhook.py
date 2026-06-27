from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook_listener():
    data = request.json
    print(data)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='192.168.29.136', port=5000, debug=True)
