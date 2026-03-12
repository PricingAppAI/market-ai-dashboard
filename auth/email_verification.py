import smtplib
import random
from email.mime.text import MIMEText


def send_verification_code(receiver_email):

    code = str(random.randint(100000, 999999))

    sender_email = "pricingapp.ai@gmail.com"
    sender_password = "pjtp bqqb yngo kfbu"

    subject = "Código de verificación - Market AI"
    body = f"Tu código de verificación es: {code}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(sender_email, sender_password)

    server.sendmail(sender_email, receiver_email, msg.as_string())

    server.quit()

    return code