import requests
import smtplib
from email.mime.text import MIMEText

# Replace these placeholders with your actual API keys and details
MARINE_TRAFFIC_API_KEY = "marine_traffic_api_key"
SMTP_SERVER = "smtp_server.com"
SMTP_PORT = 587
SMTP_USERNAME = "email@example.com"
SMTP_PASSWORD = "email_password"

def get_ship_information(ship_id):
    try:
        # Use the MarineTraffic API to get ship information
        url = f"https://api.marinetraffic.com/vesselmasterdata/v1/{ship_id}?key={MARINE_TRAFFIC_API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            ship_data = response.json()
            return ship_data
        else:
            print(f"Failed to retrieve ship information. Status Code: {response.status_code}")
            return None
    
    except requests.RequestException as e:
        print(f"Error in the request: {e}")
        return None

def craft_email(ship_data):
    if ship_data:
        # Create a personalized email content based on ship information
        email_content = f"Hello {ship_data.get('OWNER', 'Ship Owner')},\n\n"\
                        f"We noticed that your ship, {ship_data.get('SHIPNAME', 'Unknown Ship')}, is near our port at {ship_data.get('LATITUDE', 0)}, {ship_data.get('LONGITUDE', 0)}.\n"\
                        "We offer excellent maritime services that could benefit your operations.\n"\
                        "Let's discuss how we can collaborate!\n\n"\
                        "Best regards,\n"\
                        "SeaTracker Pro Team"
        return email_content
    else:
        return "Error in retrieving ship information. Please check the logs for details."

def send_email(subject, body, to_email):
    try:
        # Setup the MIME
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email

        # Establish a connection to the SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        print("Email sent successfully!")
    
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

def main():
    # Example usage:
    ship_id = "12345"  # Replace with the actual ship ID
    ship_data = get_ship_information(ship_id)
    email_content = craft_email(ship_data)

    if email_content:
        send_email("SeaTracker Pro - New Opportunity", email_content, "company@example.com")

if __name__ == "__main__":
    main()
