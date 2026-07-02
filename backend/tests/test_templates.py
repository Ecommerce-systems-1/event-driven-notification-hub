from app.templates import render_template

TEMPLATES = {
    "email_order_placed": {
        "channel": "EMAIL",
        "subject": "Your order {{order_id}} is confirmed!",
        "body_template": "Hi {{customer_name}}, order {{order_id}} placed for ${{total}}."
    }
}

def test_render_basic_substitution():
    result = render_template(
        "email_order_placed",
        {"order_id": "ORD-001", "customer_name": "Alice", "total": "49.99"},
        templates=TEMPLATES
    )
    assert "ORD-001" in result
    assert "Alice" in result
    assert "49.99" in result

def test_render_missing_key_leaves_placeholder():
    result = render_template(
        "email_order_placed",
        {"order_id": "ORD-002"},  # missing customer_name and total
        templates=TEMPLATES
    )
    assert "ORD-002" in result
    assert "{{customer_name}}" in result

def test_render_unknown_template_returns_fallback():
    result = render_template("nonexistent", {})
    assert "notification" in result.lower()