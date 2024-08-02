# email_sender.py
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders

# Load environment variables from .env file
load_dotenv()

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

def send_email(pdf_filename, plot_filename):
    email_from = EMAIL_USER
    recipient_email = EMAIL_RECIPIENT
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = EMAIL_USER
    smtp_password = EMAIL_PASSWORD

    # Create multipart message
    msg = MIMEMultipart('related')
    msg['From'] = email_from
    msg['To'] = recipient_email
    msg['Subject'] = 'PDF Report with Plot'

    # Alternative part for plain text and HTML
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    # Add plain text content
    text_body = "Please find attached the PDF report with the plot."
    msg_alternative.attach(MIMEText(text_body, 'plain'))

    # Add HTML content with embedded image
    html_body = """
    <html>
      <body>
        <p>Please find attached the PDF report with the plot.</p>
        <p><img src="cid:image1" alt="Plot"></p>
      </body>
    </html>
    """
    msg_alternative.attach(MIMEText(html_body, 'html'))

    # Attach image
    with open(plot_filename, 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<image1>')
        msg.attach(img)

    # Attach PDF report
    with open(pdf_filename, 'rb') as fp:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(fp.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
        msg.attach(attachment)
    
    # Make a local copy of what we are going to send.
    with open('outgoing.msg', 'wb') as f:
        f.write(bytes(msg))

    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(email_from, recipient_email, msg.as_string())

    print('Email sent successfully')
