from django.conf import settings
from twilio.rest import Client

def send_sos_sms(phone, latitude, longitude,user):
    """Sends an SOS alert with location using Twilio SMS API."""
    
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # Google Maps link with live location
    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    message_body = f"🚨 SOS ALERT! 🚨\nEmergency for {user.first_name} !Please help!\nLive Location: {maps_link}"

    try:
        message = client.messages.create(
            body=message_body,
            
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str("+91"+phone)
        )
        return f"Message sent successfully! SID: {message.sid}"
    
    except Exception as e:
        return f"Failed to send SMS: {str(e)}"