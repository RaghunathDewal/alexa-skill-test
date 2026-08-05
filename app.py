from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

ALEXA_SKILL_ID = "amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

RESERVATION = {
    "reservation_id": 558,
    "pms_reservation_id": "694edb6527905a875858ceec",
    "unit_name": "Bear Moon Ranch - Hot Tub, Pool, Pickleball",
    "property_id": 1,
    "property_name": "Grand Welcome Austin",
    "guest_name": "Andria",
    "checkin_date": "2026-12-24",
    "checkout_date": "2026-12-28",
    "organization_id": 2,
    "guest_count": 2,
    "unit_notes": {
        "wifi_name": "BearMoonRanch_WiFi",
        "trash_info": "Trash pickup is every Tuesday morning, bins are by the garage.",
        "wifi_password": "welcome2026"
    },
    "unit_address": {
        "full": "5103 Canyon Ranch Trail, Spicewood, TX 78669, USA",
        "city": "Spicewood",
        "state": "Texas",
        "zipcode": "78669"
    },
    "property_address": {
        "full_address": "701 Tillery St. #12 STE 147",
        "city": "Austin",
        "state": "TX",
        "zip_code": "78702"
    }
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


def format_date(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    day = d.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return d.strftime(f"%B {day}{suffix}, %Y")


# Maps normalized slot values -> a function that returns the spoken answer
def get_detail_answer(detail_type):
    r = RESERVATION
    detail_type = (detail_type or "").lower().strip()

    mapping = {
        "check in": f"Check-in is on {format_date(r['checkin_date'])}.",
        "check in date": f"Check-in is on {format_date(r['checkin_date'])}.",
        "checkin": f"Check-in is on {format_date(r['checkin_date'])}.",
        "check out": f"Check-out is on {format_date(r['checkout_date'])}.",
        "check out date": f"Check-out is on {format_date(r['checkout_date'])}.",
        "checkout": f"Check-out is on {format_date(r['checkout_date'])}.",
        "guest count": f"This reservation is booked for {r['guest_count']} guests.",
        "number of guests": f"This reservation is booked for {r['guest_count']} guests.",
        "guests": f"This reservation is booked for {r['guest_count']} guests.",
        "unit name": f"You're staying at {r['unit_name']}.",
        "unit": f"You're staying at {r['unit_name']}.",
        "property name": f"This property is managed by {r['property_name']}.",
        "property": f"This property is managed by {r['property_name']}.",
        "unit address": f"The unit address is {r['unit_address']['full']}.",
        "address": f"The unit address is {r['unit_address']['full']}.",
        "location": f"The unit address is {r['unit_address']['full']}.",
        "property address": f"The property office address is {r['property_address']['full_address']}, {r['property_address']['city']}, {r['property_address']['state']}.",
        "wifi name": (f"The WiFi network is {r['unit_notes']['wifi_name']}."
                       if r['unit_notes']['wifi_name'] else "WiFi details aren't set for this unit yet."),
        "wifi password": (f"The WiFi password is {r['unit_notes']['wifi_password']}."
                           if r['unit_notes']['wifi_password'] else "WiFi details aren't set for this unit yet."),
        "wifi": (f"The WiFi network is {r['unit_notes']['wifi_name']}, and the password is {r['unit_notes']['wifi_password']}."
                 if r['unit_notes']['wifi_name'] else "WiFi details aren't set for this unit yet."),
        "trash": r['unit_notes']['trash_info'] or "Trash information isn't available for this unit yet.",
        "trash info": r['unit_notes']['trash_info'] or "Trash information isn't available for this unit yet.",
        "reservation id": f"Your reservation ID is {r['reservation_id']}.",
        "reservation number": f"Your reservation ID is {r['reservation_id']}.",
        "guest name": f"This reservation is under the name {r['guest_name']}.",
    }

    return mapping.get(detail_type)


@app.route("/", methods=["POST"])
def alexa_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    app_id = get_app_id(data)
    if app_id != ALEXA_SKILL_ID:
        return jsonify({"error": "Invalid skill ID"}), 403

    req_type = data["request"]["type"]
    r = RESERVATION

    if req_type == "LaunchRequest":
        speech = (
            f"Hi {r['guest_name']}! Welcome back. You can ask me about your check-in "
            f"or check-out date, the address, WiFi, guest count, or your order status."
        )
        return build_response(speech, end_session=False)

    if req_type == "IntentRequest":
        intent = data["request"]["intent"]
        intent_name = intent["name"]

        if intent_name == "GetDetailIntent":
            slots = intent.get("slots", {})
            detail_slot = slots.get("DetailType", {})
            detail_value = detail_slot.get("value")

            answer = get_detail_answer(detail_value)
            if answer:
                return build_response(answer, end_session=False)
            else:
                return build_response(
                    "I'm not sure about that detail. You can ask about check-in, "
                    "check-out, address, WiFi, guest count, or trash pickup.",
                    end_session=False
                )

        if intent_name == "GetReservationIntent":
            speech = (
                f"Hi {r['guest_name']}, your reservation is at {r['unit_name']}, "
                f"managed by {r['property_name']}, for {r['guest_count']} guests. "
                f"Check-in is {format_date(r['checkin_date'])} and check-out is "
                f"{format_date(r['checkout_date'])}."
            )
            return build_response(speech, end_session=False)

        if intent_name == "GetOrderIntent":
            o = ORDER
            speech = (f"Your order {o['order_id']} for {o['item']} is currently "
                      f"{o['status']}, arriving in {o['eta']}.")
            return build_response(speech, end_session=False)

        if intent_name == "AMAZON.HelpIntent":
            return build_response(
                "You can ask about your reservation, check-in, check-out, address, "
                "WiFi, guest count, trash pickup, or your order status.",
                end_session=False
            )

        if intent_name in ("AMAZON.CancelIntent", "AMAZON.StopIntent"):
            return build_response(f"Goodbye, {r['guest_name']}! Have a great stay.")

        if intent_name == "AMAZON.FallbackIntent":
            return build_response(
                "Sorry, I didn't catch that. You can ask about your reservation details or order.",
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