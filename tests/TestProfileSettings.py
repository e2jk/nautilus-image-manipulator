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
from copy import copy
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

    @with_setup(setup_func_init_default)
    def test_addprofile(self):
        conf = Config("/tmp/nim-test.config")

        # There are 5 default profiles
        assert 5 == len(conf.profiles)

        # Create a new profile that is a copy of the first default profile.
        # It should be detected as being the same as the first profile.
        newProfile = copy(conf.profiles[0])
        assert 0 == conf.addprofile(newProfile)

        # Create a new profile that is a copy of the first default profile
        # but has a different quality. The name of both the first and the
        # new profile will be changed to contain the quality
        newProfile = copy(conf.profiles[0])
        newProfile.quality = 80
        assert _("Send small images to 1fichier.com") == conf.profiles[0].name
        assert 4 == conf.addprofile(newProfile)
        pname = _("Send %s images to 1fichier.com") + " " + _("(%d%% quality)")
        assert pname % (_("small"), 90) == conf.profiles[0].name
        assert pname % (_("small"), 80) == conf.profiles[4].name

        # Create a new profile that is a copy of the first default profile
        # but has yet another quality. The name of the first, fifth and the
        # new profile will be changed to contain the quality
        newProfile = copy(conf.profiles[0])
        newProfile.quality = 70
        assert pname % (_("small"), 90) == conf.profiles[0].name
        assert pname % (_("small"), 80) == conf.profiles[4].name
        assert 5 == conf.addprofile(newProfile)
        assert pname % (_("small"), 90) == conf.profiles[0].name
        assert pname % (_("small"), 80) == conf.profiles[4].name
        assert pname % (_("small"), 70) == conf.profiles[5].name

        # Create a new profile that is a copy of the first default profile
        # that has the same quality but a very large size. The name of the
        # first, fifth and sixth profiles should still be changed to contain
        # the quality, but the name of the new profile should be the default
        newProfile = copy(conf.profiles[0])
        newProfile.size = None
        newProfile.width = 2000
        newProfile.height = 2000
        newProfile.createname(setSelf=True)
        assert pname % (_("small"), 90) == conf.profiles[0].name
        assert pname % (_("small"), 80) == conf.profiles[4].name
        assert pname % (_("small"), 70) == conf.profiles[5].name
        assert 6 == conf.addprofile(newProfile)
        assert pname % (_("small"), 90) == conf.profiles[0].name
        assert pname % (_("small"), 80) == conf.profiles[4].name
        assert pname % (_("small"), 70) == conf.profiles[5].name
        assert conf.profiles[6].createname() == conf.profiles[6].name

        # Create a new profile that is a copy of the first default profile
        # that has the same quality and a size that's just one pixel less.
        # The default name should be the same, so both quality and size will
        # be added to the name of the first and eighth profiles
        newProfile = copy(conf.profiles[0])
        newProfile.size = None
        newProfile.width = 639
        newProfile.height = 640
        newProfile.createname(setSelf=True)
        assert pname % (_("small"), 90) == conf.profiles[0].name
        assert pname % (_("small"), 80) == conf.profiles[4].name
        assert pname % (_("small"), 70) == conf.profiles[5].name
        assert conf.profiles[6].createname() == conf.profiles[6].name
        assert 7 == conf.addprofile(newProfile)
        assert pname % (_("small") + " (640x640)", 90) == conf.profiles[0].name
        assert pname % (_("small"), 80) == conf.profiles[4].name
        assert pname % (_("small"), 70) == conf.profiles[5].name
        assert conf.profiles[6].createname() == conf.profiles[6].name
        assert pname % (_("small") + " (639x640)", 90) == conf.profiles[7].name
