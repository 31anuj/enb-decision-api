from flask import Flask, jsonify, request

app = Flask(__name__)

C_COLD = 0.000808
C_WARM = 0.000083


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/decide")
def decide():
    data = request.get_json(silent=True) or {}
    p = data.get("probability")
    if not isinstance(p, (int, float)) or isinstance(p, bool) or not 0 <= p <= 1:
        return jsonify(error="probability must be a number between 0 and 1"), 400
    enb = p * C_COLD - C_WARM
    return jsonify(action="PREWARM" if enb > 0 else "SKIP", enb=round(enb, 9), probability=p)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
