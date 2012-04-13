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

import gdata
import gdata.docs.client
from   gdata.client import BadAuthentication


def create_docs_client(ui, app_name, auth_tries=3, always_prompt_credentials=False):
    client = gdata.docs.client.DocsClient(source=app_name)
    client.ssl = True
    bad_credential = always_prompt_credentials
    for i in range(auth_tries):
        user, password = ui.get_credentials(bad_credential=bad_credential, service="Google Docs")
        try:
            client.ClientLogin(user, password, source=app_name)
        except BadAuthentication, e:
            bad_credential = True
            continue
        return client
    raise ("Failed authentication %s times."%auth_tries)

