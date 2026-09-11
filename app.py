import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import razorpay

app = Flask(__name__)

# Enable CORS so your frontend HTML can communicate with this API
CORS(app)

# Fetch credentials securely from environment variables
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

# Initialize Razorpay Client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Backend service running"}), 200

@app.route("/create-order", methods=["POST"])
def create_order():
    try:
        data = request.get_json() or {}
        amount = data.get("amount", 50000)  # Amount in subunits (e.g., 50000 paise = ₹500)
        currency = data.get("currency", "INR")

        order_data = {
            "amount": amount,
            "currency": currency,
            "receipt": f"receipt_{os.urandom(4).hex()}",
            "payment_capture": 1
        }
        
        # Create Razorpay Order
        order = client.order.create(data=order_data)
        return jsonify(order), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify-payment", methods=["POST"])
def verify_payment():
    try:
        data = request.get_json()
        
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }

        # Verify signature using Razorpay SDK
        client.utility.verify_payment_signature(params_dict)
        return jsonify({"status": "success", "message": "Payment verified successfully"}), 200

    except razorpay.errors.SignatureVerificationError:
        return jsonify({"status": "failure", "message": "Invalid payment signature"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
