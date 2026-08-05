# app.py
from flask import Flask, render_template
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from flask_ask_sdk.skill_adapter import SkillAdapter

app = Flask(__name__)
sb = SkillBuilder()

# Mock data
RESERVATION = {
    "name": "sample reservation",
    "date": "August 10th",
    "time": "7 PM",
    "guests": "2 guests",
    "location": "Downtown branch"
}

ORDER = {
    "order_id": "ORD1234",
    "item": "wireless headphones",
    "status": "shipped",
    "eta": "2 days"
}

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech = "Welcome! You can ask me about your reservation or your order."
        return handler_input.response_builder.speak(speech).ask(speech).response

class GetReservationIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetReservationIntent")(handler_input)

    def handle(self, handler_input):
        r = RESERVATION
        speech = (f"Your reservation is for {r['guests']} on {r['date']} "
                  f"at {r['time']}, at {r['location']}.")
        return handler_input.response_builder.speak(speech).response

class GetOrderIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetOrderIntent")(handler_input)

    def handle(self, handler_input):
        o = ORDER
        speech = (f"Your order {o['order_id']} for {o['item']} is currently "
                  f"{o['status']}, arriving in {o['eta']}.")
        return handler_input.response_builder.speak(speech).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech = "You can ask about your reservation or your order status."
        return handler_input.response_builder.speak(speech).ask(speech).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speech = "Goodbye!"
        return handler_input.response_builder.speak(speech).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetReservationIntentHandler())
sb.add_request_handler(GetOrderIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

skill_adapter = SkillAdapter(skill=sb.create(), skill_id="amzn1.ask.skill.878d739f-cf0e-4a7c-ad7c-c2bc5143bffc", app=app)

@app.route("/", methods=["POST"])
def invoke_skill():
    return skill_adapter.dispatch_request()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)