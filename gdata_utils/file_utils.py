# Helper utils for gdata.
# 
# Copyright (C) 2012 NigelB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from StringIO import StringIO
from pprint import pprint
import os


class GoogleDocsConfig:
    """A Config file stored in Google Docs"""

    def __init__(self, ui, service_name, file_title, mime_type="text/plain"):
        from gdata.docs.client import DocsClient
        self.service_name = service_name
        self.client = DocsClient(source=service_name)
        self.client.ssl = True
        self.file_title = file_title
        self.ui = ui
        self.mime_type = mime_type
        self.__authenticate()
        self.__read()


    def getClient(self):
        return self.client

    def __read(self):
        import gdata.docs.client as client
        feed = self.client.GetDocList(
                uri='%s?title=%s&title-exact=true&max-results=1' % (client.DOCLIST_FEED_URI, self.file_title))
        if not feed.entry:
            self.config_entry = None
            self.config = {}
            self.write_config()
        else:
            self.config_entry = feed.entry[0]
            a = {}
            exec(self.client.GetFileContent(self.config_entry.content.src), a)
            self.config = a['config']

    def write_config(self):
        from gdata.client import ResumableUploader
        from gdata.docs.data import DocsEntry

        from atom.data import Title
        out = StringIO()
        out.write("config=")
        pprint(self.config, out, 4)
        uni = unicode(out.getvalue())
        out.close()
        out = StringIO(uni.encode("utf-8"))
        length = len(out.getvalue())
        uploader = ResumableUploader(self.client, out, self.mime_type, length, chunk_size=length, desired_class=DocsEntry)
        entry = DocsEntry(title=Title(text=self.file_title))
        if self.config_entry is None:
            self.config_entry = uploader.UploadFile('/feeds/upload/create-session/default/private/full', entry=entry)
        else:
             self.config_entry = uploader.UpdateFile(self.config_entry.get_link("http://schemas.google.com/g/2005#resumable-edit-media").href, force=True)


    def __authenticate(self):
        from gdata.client import BadAuthentication
        username, password = self.ui.get_credentials()
        while True:
            try:
                self.client.ClientLogin(username, password, source=self.service_name)
                break
            except BadAuthentication, be:
                username, password = self.ui.get_credentials(bad_credential=True)


    def get(self, key):
        return self.config[key]
    __getitem__ = get


    def set(self, key, value):
        self.config[key] = value
    __setitem__ = set

    def has_key(self, key):
        return self.config.has_key(key)

    def delete(self, key):
        del self.config[key]
    __delitem__ = delete

    def keys(self):
        return self.config.keys()
