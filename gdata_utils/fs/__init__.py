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
import os
import atom.core
import gdata.media, gdata.client, gdata.docs.data
from gdata_utils.fs.constants import *
from simpleui.utils import UserConfig



class GoogleDocs:
    def __init__(self, client, cache_dir):
        self.client = client
        self.config = UserConfig(dir_name=cache_dir, config_file="cache", def_config_callback=lambda x:{})
        self.cache_dir = cache_dir
        if not self.config.read_config():
            self.config.initialize_dir(None)

    def getFolders(self):
        folders = self.get_list('/feeds/default/private/full/-/folder')
        if not folders.entry:
            return None
        return [Folder(self, x) for x in folders.entry]

    def getFolder(self, descriptor, etag=None):
        return Folder(self, self.client.get_doc(descriptor[id], etag=etag))

    def __cached_entry(self, id):
        return os.path.join(self.cache_dir, id)

#    def get_list(self, url, eid=None):
#        config = self.config
#        ietag = None
#
#
#        if config.has_key(url):
#            ietag=config[url][etag]
#        feed = self.__get_list(url,etag=ietag)
#
#        if not ietag:
#            cache_entry = open(self.__cached_entry(config[url][file_name]), "r")
#            data = cache_entry.read()
#            cache_entry.close()
#            name="clzz"
#            into={}
#            exec(config[url][desired_class]%name, into)
#            return atom.core.parse(data,target_class=into[name])
#        else:
#
#            id = eid
#            if not eid:
#                id=feed.id.text
#                for cat in feed.category:
#                    if cat.term == item_type:
#                        id="root"
#                    else:
#                        pass
#                print id
#
#            cache_entry = open(self.__cached_entry(id), "wb")
#            cache_entry.write(feed.__str__())
#            cache_entry.close()
#        config[url] = {etag:feed.etag, id:feed.id.text, file_name:self.__cached_entry(id),
#                       desired_class:"from %s import %s as %s"%(feed.__class__.__module__,feed.__class__.__name__,"%s")}
#        config.write_config()
#        return feed

    def get_list(self, url):
        feed = self.client.GetDocList(uri=url)
        if not feed.entry:
            raise Exception
        if feed.GetNextLink():
            feed.entry += self.get_list(feed.GetNextLink().href).entry
        return feed

    def get_cache_descriptor(self, id):
        if self.config.has_key(id): self.config[id]
        return None

    def open_cached_file(self, id, mode=None, buffering=None):
        return open(self.__cached_entry(id), mode=mode, buffering=buffering)

    def download(self, id, extra_params=None):
        item_etag = None
        if self.config.has_key(id):
            item_etag = self.config[id][etag]
        entry = self.client.GetDoc(id, item_etag)
        self.client.Download(entry, self.__cached_entry(id), extra_params=extra_params)
        self.config[id] = create_descriptor(entry)
        self.config.write_config()

    def create(self, title, folder_entry, mime_type="text/plain"):
#        entry = self.client.create("file", title, folder_or_id=folder_or_id, writers_can_invite=writers_can_invite,
#            auth_token=auth_token, uri=uri, **kwargs)
        ms = gdata.data.MediaSource(file_handle=StringIO(), content_type="text/plain", content_length=0)
        entry = self.client.Upload(ms, title, folder_or_uri=folder_entry)
#        self.config[entry.resource_id.text] = create_descriptor(entry)
#        self.config.write_config()
#        return entry
#        entry = gdata.docs.data.DocsEntry(title=atom.data.Title(text=title))
#        entry.category.append(gdata.docs.data.make_kind_category('file'))
        return entry

    def write(self, entry, stream, length, mime_type="text/plain"):
#        entry = self.client.GetDoc(entry.resource_id.text)
#        doc = gdata.docs.data.Resource(type='document', title='My Sample Doc')

#        ms = gdata.data.MediaSource(file_handle=stream, content_type=mime_type, content_length=length)
#        updated_entry = self.client.Update(entry, media_source=ms)
        upl = gdata.client.ResumableUploader(self.client, stream, mime_type, length)
        upl.update_file(entry, force=True)


def create_descriptor(entry):
    return{
        title: entry.title.text.encode('UTF-8'),
        etag: entry.etag,
        id: entry.resource_id.text,
        mime: entry.content.type,
        }

class GD:
    def title(self):
        return self.entry.title.text.encode('UTF-8')

    def getID(self):
        return self.entry.resource_id.text

    def createDescriptor(self):
        return create_descriptor(self.entry)

class Folder(GD):
    def __init__(self, fs, entry):
        self.fs = fs
        self.entry = entry

    def list(self):
        feed = self.fs.get_list("%s/%s" % (self.entry.GetSelfLink().href, "contents"))
        toRet = []
        for item in feed.entry:
            for category in item.category:
                if category.term == folder_type:
                    toRet.append(Folder(self.fs, item))
                elif category.term == file_type:
                    toRet.append(File(self.fs, item))
        return toRet

    def __repr__(self):
        return self.title()


    def create_file(self, name, mime_type="text/plain"):
        return File(self.fs, self.fs.create(name, folder_entry=self.entry, mime_type=mime_type))

    def get_file(self, name):
        for itm in self.list():
            print itm.title() ,name, itm.title() == name
            if itm.__class__ == File and itm.title() == name:
                itm.download()
                return itm
        return None

class File(GD):
    def __init__(self, fs, entry):
        self.fs = fs
        self.entry = entry

    def getID(self):
        return self.entry.resource_id.text

    def open(self, mode=None, buffering=None):
        return self.fs.open_cache_file(self.getID(), mode=mode, buffering=buffering)

    def write(self, stream, length, mime_type="text/plain"):
        self.fs.write(self.entry, stream, length, mime_type=mime_type)


    def download(self):
        extra_params = None
        mime_type = self.entry.content.type
#        if parent and mime_type != self.parent_mime_type:
#            extra_params = {'exportFormat': "txt"}

        self.fs.download(self.getID(), extra_params=extra_params)

#        entry = self.client.GetDoc(item['file'], current_descriptor[etag])
#        if extra_params is None:
#            self.client.Download(entry, item_loc)
#        else:
#            self.client.Download(entry, item_loc, extra_params
