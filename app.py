import streamlit as st
import razorpay

# Access live credentials securely from Streamlit Secrets
RAZORPAY_KEY_ID = st.secrets["RAZORPAY_KEY_ID"]
RAZORPAY_KEY_SECRET = st.secrets["RAZORPAY_KEY_SECRET"]

# Initialize the Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

st.set_page_config(page_title="Subscription Gateway", layout="centered")

st.title("Fin. India Holdings Premium Subscription")
st.write("Enter your details below to access the MF Stock Price Ribbon and 24/7 Consumer Chat.")

# Create the user input form
with st.form("subscription_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    submitted = st.form_submit_button("Proceed to Payment")

if submitted:
    if not name or not email or not phone:
        st.error("Please fill in all details before proceeding.")
    else:
        try:
            # Generate a dynamic payment link securely on the server-side
            payment_link = client.payment_link.create({
                "amount": 50000,  # Amount in paise (₹500.00)
                "currency": "INR",
                "accept_partial": False,
                "description": "Premium Mutual Fund Subscription",
                "customer": {
                    "name": name,
                    "email": email,
                    "contact": phone
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True
            })
            
            st.success("Secure payment portal generated successfully!")
            
            # Display a direct button that routes the user to Razorpay's secure checkout
            st.link_button("👉 Click Here to Complete Payment", payment_link["short_url"], type="primary")

        except Exception as e:
            st.error(f"Transaction initialization failed: {str(e)}")
