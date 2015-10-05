import os
import os.path
import re
import unicodedata

class Backend(object):

    def __init__(self, config):
        self.path = config["path"]
        if not os.path.exists(self.path):
            raise Exception("Specificed path does not exist")

    def new_collection(self):
        return DocumentCollection(self)


class DocumentCollection(object):

    def __init__(self, backend):
        self.backend = backend

    def set_metadata(self, subject, sender, date):
        foldername = "%s %s %s" % (date, sender, subject)
        foldername = unicodedata.normalize('NFKD', foldername).lower()
        foldername = re.sub(r'\W+', '_', foldername)
        self.fullpath = os.path.abspath(os.path.join(self.backend.path, foldername))
        os.mkdir(self.fullpath)

    def attach(self, filename, mimetype, binary):
        filename = os.path.join(self.fullpath, filename)
        with file(filename, "wb") as f:
            f.write(binary)

    def execute(self):
        pass