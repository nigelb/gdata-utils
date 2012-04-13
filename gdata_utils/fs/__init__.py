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


class GoogleDocs:
    def __init__(self, client):
        self.client = client

    def getFolders(self):
        folders = self.__get_list('/feeds/default/private/full/-/folder')
        if not folders.entry:
            return None
        return [Folder(self, x) for x in folders.entry]

    def __get_list(self, url):
        feed = self.client.GetDocList(uri=url)
        if not feed.entry:
            raise Exception
        if feed.GetNextLink():
            feed.entry += self.__get_list(feed.GetNextLink().href).entry
        return feed


class Folder:
    def __init__(self, fs, entry):
        self.fs = fs
        self.entry = entry

    def title(self):
        return self.entry.title.text.encode('UTF-8')

    def createDescriptor(self):
        entry = self.entry
        return{
            'title': self.title(),
            'etag': entry.etag,
            'href': entry.GetSelfLink().href,
            'file': entry.resource_id.text,
            'mime': entry.content.type,
            }


    def __repr__(self):
        return self.title()