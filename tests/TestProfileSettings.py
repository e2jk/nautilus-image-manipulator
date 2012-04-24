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

import os
from nose.tools import with_setup
from nautilus_image_manipulator.ProfileSettings import Config

import gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class TestConfig(object):
    def test_config(self):
        """Test the value of the predefined sizes"""
        size = Config.size
        assert (640, 640) == size["small"]
        assert (1280, 1280) == size["large"]

    def setup_func_init_default(self):
        "Make sure there is no saved profile in /tmp/nim-test.config"
        os.remove("/tmp/nim-test.config")

    @with_setup(setup_func_init_default)
    def test_init_default(self):
        """Test the creation of the default configuration"""
        conf = Config("/tmp/nim-test.config")

        # There are 5 default profiles
        assert 5 == len(conf.profiles)

        # The current version of the profile 
        assert 2 == conf.actualversion

        # The 1st default profile
        p = conf.profiles[0]
        assert _("Send %s images to 1fichier.com") % _("small") == p.name
        assert "small" == p.size
        assert 90 == p.quality
        assert "upload" == p.destination
        assert "%s.zip" % _("resized") == p.zipname
        assert "1fichier.com" == p.url

        # The 2nd default profile
        #TODO

        # The 3rd default profile
        #TODO

        # The 4th default profile
        #TODO

        # The default custom profile
        #TODO
