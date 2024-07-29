from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import csv
from email.message import EmailMessage
import ssl
import smtplib
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

email_sender = os.getenv("EMAIL_SENDER")
email_password = os.getenv("EMAIL_PASSWORD")

subject = "Offer Letter"

context = ssl.create_default_context()

def generate_offer_letter(employee_name):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Draw the content on the PDF
    can.drawString(100, 750, f"Dear {employee_name},")
    can.drawString(100, 730, "We are delighted to extend our warmest Congratulations to you for")
    can.drawString(100, 710, "your selection into the GBJ BUZZ Internship Program.")
    # ... (more lines from the provided template)
    can.drawString(100, 150, "Best regards,")
    can.drawString(100, 130, "Your Company")
    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)

    return packet

@app.route('/send-emails', methods=['POST'])
def send_emails():
    if 'csvFile' not in request.files:
        app.logger.error("No file part in request")
        return jsonify(message="No file part"), 400

    file = request.files['csvFile']
    if file.filename == '':
        app.logger.error("No selected file")
        return jsonify(message="No selected file"), 400

    try:
        file_content = file.stream.read().decode('utf-8').splitlines()
        reader = csv.DictReader(file_content)
        if not reader.fieldnames or 'name' not in reader.fieldnames or 'email' not in reader.fieldnames:
            app.logger.error("Invalid CSV file headers")
            return jsonify(message="Invalid CSV file headers"), 400

        for row in reader:
            name = row['name']
            email_receiver = row['email']

            # Generate a customized offer letter
            offer_letter_pdf = generate_offer_letter(name)

            # Create the email content for each employee
            body = f"""
            Dear {name},

            We are pleased to offer you a position at our company. Please find the details attached.

            Best regards,
            Your Company
            """

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            # Attach the PDF
            em.add_attachment(offer_letter_pdf.getvalue(), maintype='application', subtype='pdf', filename=f"{name}_Internship_Offer_Letter.pdf")

            # Send the email
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, email_receiver, em.as_string())
                app.logger.info(f"Email sent to {email_receiver}")
            except Exception as e:
                app.logger.error(f"Error sending email to {email_receiver}: {e}")
                return jsonify(message=f"Error sending email to {email_receiver}: {e}"), 500

        app.logger.info("Emails sent successfully")
        return jsonify(message="Emails sent successfully"), 200

    except Exception as e:
        app.logger.error(f"Failed to read the file: {e}")
        return jsonify(message=f"Failed to read the file: {e}"), 500

if __name__ == '__main__':
    app.run(debug=True)
