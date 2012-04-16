#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010-2012 Emilien Klein <emilien _AT_ klein _DOT_ st>
# 
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from nautilus_image_manipulator.upload.poster import version as poster_version

class TestPoster(object):
    def test_version(self):
        # Make sure Poster's version is new enough. Versions before 0.8.0
        # contain a bug that make it unusable for our purpose.
        # See https://bitbucket.org/chrisatlee/poster/changeset/8d102e3679cf
        assert (0, 8, 0) <= poster_version
