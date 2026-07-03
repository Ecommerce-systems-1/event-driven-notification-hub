import re

SEED_TEMPLATES = {
    "email_order_placed": {
        "subject": "Your order {{order_id}} is confirmed!",
        "body_template": "Hi {{customer_name}}, your order {{order_id}} has been placed. Total: ${{total}}."
    },
    "sms_order_placed": {
        "subject": "",
        "body_template": "Order {{order_id}} confirmed! Total ${{total}}. -ShopCo"
    },
    "push_order_placed": {
        "subject": "Order Confirmed",
        "body_template": "Your order {{order_id}} is on its way!"
    },
    "email_payment_captured": {
        "subject": "Payment received for {{order_id}}",
        "body_template": "Hi {{customer_name}}, we received your payment of ${{amount}} for order {{order_id}}."
    },
    "email_order_shipped": {
        "subject": "Your order {{order_id}} has shipped!",
        "body_template": "Hi {{customer_name}}, order {{order_id}} shipped via {{carrier}}. Tracking: {{tracking_number}}."
    },
    "sms_order_shipped": {
        "subject": "",
        "body_template": "Shipped! Order {{order_id}} via {{carrier}}. Track: {{tracking_number}}"
    },
    "email_delivery_confirmed": {
        "subject": "Order {{order_id}} delivered",
        "body_template": "Hi {{customer_name}}, order {{order_id}} was delivered. Enjoy!"
    },
    "email_return_requested": {
        "subject": "Return request received for {{order_id}}",
        "body_template": "Hi {{customer_name}}, we received your return request {{return_id}} for order {{order_id}}."
    },
}

def render_template(template_id: str, payload: dict, templates: dict = None) -> str:
    tmpl_store = templates or SEED_TEMPLATES
    tmpl = tmpl_store.get(template_id)
    if not tmpl:
        return f"You have a new notification regarding order {payload.get('order_id', 'N/A')}."
    body = tmpl["body_template"]
    for key, value in payload.items():
        body = body.replace("{{" + key + "}}", str(value))
    return body