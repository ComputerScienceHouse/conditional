import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from datetime import date
from conditional import app

def send_absent_hm_attendance_emails(absent_members):
    today_date = date.today().strftime("%m/%d")
    subject = "You were marked as absent for the {} House Meeting.".format(today_date)
    body = subject + "\n\nIf this is a mistake please message the evaluations director and let them know."
    # doing this uses the same connection for all emails sent to absent members
    send_email(absent_members, subject, body)

def send_present_hm_attendance_email(member):
    today_date = date.today().strftime("%m/%d")
    subject = "You were marked as present for the {} House Meeting.".format(today_date)
    body = subject
    send_email([member], subject, body)

def send_attenance_requirement_met_email(user):
    subject = "You have attended 30 Directorship Meetings"
    body = """You have met one of the requirements of active 
                membership by attending 30 directorship meetings. 
                Congratulations or I'm Sorry!"""
    send_email([user], subject, body)

def send_email(members, subject, body):
    """A function capable of sending one or many emails"""
    debug_email = app.config['DEBUG_EMAIL']
    should_send_email = app.config['SEND_EMAIL']

    if should_send_email:
        recipents = map("{}@csh.rit.edu".format, members)
        server = smtplib.SMTP(app.config['MAIL_SERVER'])
        server.starttls()
        server.login('conditional', app.config['EMAIL_PASSWORD'])
        sender_addr = "conditional@csh.rit.edu"
        for member in recipents:
            msg = MIMEMultipart()
            if debug_email is not None:
                recipient_addr = debug_email
            else:
                recipient_addr = "{}@csh.rit.edu".format(member)
            msg["To"] = recipient_addr
            msg["From"] = sender_addr
            msg["Subject"] = subject
            msg["Date"] = formatdate(localtime=True)
            msg.attach(MIMEText(body, 'plain'))
            server.sendmail(sender_addr, recipient_addr, msg.as_string())
        server.quit()
