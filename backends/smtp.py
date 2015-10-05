import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders


class Backend(object):

    def __init__(self, config):
        self.mailto = config["to"]
        self.mailfrom = config["from"]
        self.mailserver = config["server"]

    def new_collection(self):
        return DocumentCollection(self)


class DocumentCollection(object):

    def __init__(self, backend):
        self.backend = backend
        self.msg = MIMEMultipart()
        self.msg['To'] = backend.mailto
 
    def set_metadata(self, subject, sender, date):
        self.msg['Subject'] = subject 
        self.msg['From'] = self.backend.mailfrom % sender

    def attach(self, filename, mimetype, binary):   
        part = MIMEBase(*mimetype.split("/"))
        part.set_payload(binary)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
        self.msg.attach(part)

    def execute(self):
        server = smtplib.SMTP(self.backend.mailserver)
        server.sendmail(self.backend.mailfrom % sender, self.backend.mailto, self.msg.as_string())
        