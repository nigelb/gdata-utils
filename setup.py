#!/usr/bin/env python
# Helper utils for gdata
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

from distutils.core import setup

setup(name='gdata-utils',
      version='0.0.1',
      description='Helper utils for gdata',
      author='NigelB',
      author_email='nigel.blair+gdata-utils@gmail.com',
      url='http://github.com/nigelb/gdata-utils/',
      packages=["gdata_utils", "gdata_utils.fs"],
      requires=["simpleui", "gdata (>=2.0.16)"],
     )
