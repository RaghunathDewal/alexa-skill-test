# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

# ⚠️ Replace with your actual Skill ID from the Developer Console
# (Endpoint page, or top of the skill's Build page)
ALEXA_SKILL_ID = "amzn1.ask.skill.878d739f-cf0e-4a7c-ad7c-c2bc5143bffc"

# Mock data
RESERVATION = {
    "guests": "2 guests",
    "date": "August 10th",
    "time": "7 PM",
    "location": "Downtown branch"
}

ORDER = {
    "order_id": "ORD1234",
    "item": "wireless headphones",
    "status": "shipped",
    "eta": "2 days"
}


def build_response(speech_text, end_session=True):
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": speech_text},
            "shouldEndSession": end_session
        }
    })


def get_app_id(data):
    return (
        data.get("session", {}).get("application", {}).get("applicationId")
        or data.get("context", {}).get("System", {}).get("application", {}).get("applicationId")
    )


@app.route("/", methods=["POST"])
def alexa_endpoint():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    app_id = get_app_id(data)
    if app_id != ALEXA_SKILL_ID:
        return jsonify({"error": "Invalid skill ID"}), 403

    req_type = data["request"]["type"]

    if req_type == "LaunchRequest":
        return build_response(
            "Welcome! You can ask me about your reservation or your order.",
            end_session=False
        )

    if req_type == "IntentRequest":
        intent_name = data["request"]["intent"]["name"]

        if intent_name == "GetReservationIntent":
            r = RESERVATION
            speech = (f"Your reservation is for {r['guests']} on {r['date']} "
                      f"at {r['time']}, at {r['location']}.")
            return build_response(speech)

        if intent_name == "GetOrderIntent":
            o = ORDER
            speech = (f"Your order {o['order_id']} for {o['item']} is currently "
                      f"{o['status']}, arriving in {o['eta']}.")
            return build_response(speech)

        if intent_name == "AMAZON.HelpIntent":
            return build_response(
                "You can ask about your reservation or your order status.",
                end_session=False
            )

        if intent_name in ("AMAZON.CancelIntent", "AMAZON.StopIntent"):
            return build_response("Goodbye!")

        if intent_name == "AMAZON.FallbackIntent":
            return build_response(
                "Sorry, I didn't catch that. You can ask about your reservation or order.",
                end_session=False
            )

    if req_type == "SessionEndedRequest":
        return jsonify({"version": "1.0", "response": {}})

    return build_response("Sorry, I didn't understand that.", end_session=False)


@app.route("/", methods=["GET"])
def health_check():
    return "Alexa skill backend is running", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)