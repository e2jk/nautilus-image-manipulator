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

from nose.tools import raises
from gi.repository import GObject
from nautilus_image_manipulator.ImageManipulations import ImageManipulations
from nautilus_image_manipulator.ProfileSettings import Profile

class TestImageManipulations(object):
    def test_init(self):
        files = ["/tmp/nim-test-dummy2/nonexisting.jpg"]
        p = Profile(percent=50,
                             quality=90,
                             destination="folder",
                             foldername="blabla")

        # Verify that the subdirectory name input is properly cleaned
        im = ImageManipulations(None, files, p)
        assert "blabla" == p.foldername

        p.foldername = "bla/bla"
        im = ImageManipulations(None, files, p)
        assert "bla/bla" == p.foldername

        p.foldername = "/bla/bla/"
        im = ImageManipulations(None, files, p)
        assert "bla/bla" == p.foldername

    @raises(IOError)
    def test_resize_one_image_nonexisting(self):
        """Resizing a non existing image throws an exception"""
        files = ["/tmp/nim-test-dummy2/nonexisting.jpg"]
        p = Profile(percent=50,
                             quality=90,
                             destination="folder",
                             foldername="blabla")
        im = ImageManipulations(None, files, p)
        im.resize_one_image(files[0])
