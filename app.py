import streamlit as st
import streamlit.components.v1 as components
import razorpay
import os


# 1. Initialize Razorpay using standard Environment Variables
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

st.set_page_config(page_title="F11 Finwise Premium", layout="centered")

# 2. Check for Razorpay Callback Parameters (Post-Payment)
query_params = st.query_params

if "razorpay_payment_id" in query_params and "razorpay_order_id" in query_params and "razorpay_signature" in query_params:
    try:
        # Cryptographically verify the signature server-side
        client.utility.verify_payment_signature({
            'razorpay_order_id': query_params["razorpay_order_id"],
            'razorpay_payment_id': query_params["razorpay_payment_id"],
            'razorpay_signature': query_params["razorpay_signature"]
        })
        
        # Mark user session as Premium
        st.session_state["premium_active"] = True
        st.success("✅ Payment verified successfully! Welcome to F11 Finwise Premium.")
        
        # Clear URL parameters for a clean look
        st.query_params.clear()
        
    except razorpay.errors.SignatureVerificationError:
        st.error("❌ Payment verification failed. Please contact Fin. India Holdings support.")

# 3. App Routing
if st.session_state.get("premium_active", False):
    # --- PREMIUM DASHBOARD ---
    st.header("📈 F11 Finwise Premium Dashboard")
    st.write("Welcome to the exclusive MF Stock Price Ribbon and 24/7 Consumer Chat.")
    st.info("Your premium features and analytics go here.")
    # Add your protected React Native/Python visualizations here
    
else:
    # --- SUBSCRIPTION CHECKOUT ---
    st.title("Subscribe to F11 Finwise Premium")
    st.write("Get lifetime access for a **₹500 one-time payment**.")
    
    with st.form("subscription_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        submitted = st.form_submit_button("Generate Secure Payment Portal")
        
    if submitted:
        if not name or not email or not phone:
            st.error("Please fill in all details before proceeding.")
        else:
            try:
                # Generate a unique Order ID securely on the Python backend
                order = client.order.create({
                    "amount": 50000,  # Amount in paise (₹500)
                    "currency": "INR",
                    "payment_capture": 1
                })
                
                # Razorpay will redirect to this Streamlit URL after payment via GET
                CALLBACK_URL = "https://finwise-3.onrender.com"
                
                # Render the Razorpay Checkout Modal
                checkout_html = f"""
                <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
                <div style="text-align: center; margin-top: 20px;">
                    <button id="rzp-button" style="background-color:#4caf50;color:white;padding:12px 24px;border:none;border-radius:4px;cursor:pointer;font-size:16px;font-weight:bold;width:100%;">
                        Pay ₹500 Securely
                    </button>
                </div>
                <script>
                    var options = {{
                        "key": "{RAZORPAY_KEY_ID}",
                        "amount": "{order['amount']}",
                        "currency": "{order['currency']}",
                        "name": "Fin. India Holdings",
                        "description": "F11 Finwise Premium Subscription",
                        "order_id": "{order['id']}",
                        "callback_url": "{CALLBACK_URL}",
                        "callback_method": "get",
                        "prefill": {{
                            "name": "{name}",
                            "email": "{email}",
                            "contact": "{phone}"
                        }},
                        "theme": {{
                            "color": "#4caf50"
                        }}
                    }};
                    var rzp1 = new Razorpay(options);
                    document.getElementById('rzp-button').onclick = function(e){{
                        rzp1.open();
                        e.preventDefault();
                    }}
                </script>
                """
                
                # Display the checkout button natively in Streamlit
                st.write("Order generated successfully! Click below to complete your transaction:")
                components.html(checkout_html, height=100)
                
            except Exception as e:
                st.error(f"Failed to initialize payment gateway: {e}")
