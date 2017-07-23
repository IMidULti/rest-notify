import json
import falcon
import smtplib

from smtplib import SMTPException
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

corp_email_server = 'mail.example.com'
corp_email_port = 587
corp_email_name = "My Company"
corp_email_sentfrom = 'donotreply@example.com'
corp_email_password = 'changeme'


class EmailMessage(object):
    def __init__(self):
        pass

    def send_email(self, email_to, email_to_name, email_subject, email_message):
        smtp_connection = self.get_smtp_connection(corp_email_server, corp_email_port,
                                                   corp_email_sentfrom, corp_email_password)
        if not smtp_connection:
            return False
        meme_msg = self.build_meme_body(corp_email_sentfrom, corp_email_name, email_to,
                                        email_to_name, email_subject, email_message)
        smtp_rtn = self.send_meme(smtp_connection, corp_email_sentfrom, email_to, meme_msg)
        if not smtp_rtn:
            return False
        return True

    def get_smtp_connection(self, email_server, email_port, email_user, email_password, starttls=True):
        try:
            smtp_connection = smtplib.SMTP(email_server, email_port)
            if starttls:
                smtp_connection.starttls()
            smtp_connection.login(email_user, email_password)
            print "Connected to mail server"
            return smtp_connection
        except SMTPException, e:
            print "Error: unable to send email"
        return False

    def build_meme_body(self, email_from, email_from_name, email_to, email_to_name, email_subject, email_message):
        msg = MIMEMultipart()
        msg['From'] = "%s <%s>" % (email_from_name, email_from)
        msg['To'] = "%s <%s>" % (email_to_name, email_to)
        msg['Subject'] = email_subject
        html_message = """<html>
<head>
    <style>
        h1 {
            color: navy;
            margin-left: 20px;
        }
    </style>
</head>
  <body>
    <h1>Hi!</h1>
       %s<br><br>
    </p>
  </body>
</html>""" % email_message
        msg.attach(MIMEText(html_message, 'html'))
        return msg

    def send_meme(self, smtp_connection, email_sent_from, email_to, meme_msg):
        try:
            smtp_connection.sendmail(email_sent_from, email_to, meme_msg.as_string())
            print 'Mail sent'
            return True
        except SMTPException, e:
            print 'Mail could not be sent %s' % e
            return False


class NotifyResource:
    def on_post(self, req, resp):
        try:
            msg_body = json.loads(req.stream.read())
        except ValueError:
            resp.body = '{"msg": "Invalid JSON"}'
            resp.status = falcon.HTTP_400
            return
        email_message = EmailMessage()
        email_rtn = email_message.send_email(msg_body['email'], msg_body['name'],
                                             msg_body['subject'], msg_body['msg'])
        if not email_rtn:
            resp.body = '{"msg": "Sending Mail Failed"}'
            resp.status = falcon.HTTP_500
            return


app = falcon.API()
notify = NotifyResource()
app.add_route('/notify', notify)
