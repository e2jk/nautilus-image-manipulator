#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010-2013 Emilien Klein <emilien _AT_ klein _DOT_ st>
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
from nautilus_image_manipulator.ProfileSettings import Config, Profile

import gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

configFile = "/tmp/nim-test.config"

class TestConfig(object):
    def test_config(self):
        """Test the value of the predefined sizes"""
        size = Config.size
        assert (640, 640) == size["small"]
        assert (1280, 1280) == size["large"]

    def test_init_default(self):
        """Test the creation of the default configuration"""
        # Make sure there is no saved profile in /tmp/nim-test.config
        if os.path.isfile(configFile):
            os.remove(configFile)
        assert False == os.path.isfile(configFile)
        conf = Config(configFile)

        # There are 5 default profiles
        assert 5 == len(conf.profiles)

        # The current version of the profile 
        assert 2 == conf.actualversion

        # The 1st default profile
        p = conf.profiles[0]
        assert p.name == _("Send %(imageSize)s images to %(uploadUrl)s") % {"imageSize": _("small"), "uploadUrl": "1fichier.com"}
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

    def test_addprofile(self):
        # Make sure there is no saved profile in /tmp/nim-test.config
        if os.path.isfile(configFile):
            os.remove(configFile)
        assert False == os.path.isfile(configFile)
        conf = Config(configFile)

        # There are 5 default profiles
        assert 5 == len(conf.profiles)

        up = "1fichier.com"

        # Create a new profile that is a copy of the first default profile.
        # It should be detected as being the same as the first profile.
        newProfile = copy(conf.profiles[0])
        assert 0 == conf.addprofile(newProfile)

        # Create a new profile that has the same properties as the first
        # default profile, except that it's size is defined as custom with
        # the small values. It should be detected as being the same as the
        # first profile.
        newProfile = Profile(name=_("Send %(imageSize)s images to %(uploadUrl)s") % {
                                    "imageSize": _("small"),
                                    "uploadUrl": up},
                             width=640,
                             height=640,
                             quality=90,
                             destination="upload",
                             zipname="%s.zip" % _("resized"),
                             url=up)
        assert 0 == conf.addprofile(newProfile)

        # Create a new profile that is a copy of the first default profile
        # but has a different quality. The name of both the first and the
        # new profile will be changed to contain the quality
        newProfile = copy(conf.profiles[0])
        newProfile.quality = 80
        assert conf.profiles[0].name == _("Send %(imageSize)s images to %(uploadUrl)s") % {"imageSize": _("small"), "uploadUrl": up}
        assert 4 == conf.addprofile(newProfile)
        pname = _("Send %(imageSize)s images to %(uploadUrl)s") + " " + _("(%d%% quality)")
        pname = pname.replace("%d%%", "%(quality)d%%")
        assert conf.profiles[0].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 90}
        assert conf.profiles[4].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 80}

        # Create a new profile that is a copy of the first default profile
        # but has yet another quality. The name of the first, fifth and the
        # new profile will be changed to contain the quality
        newProfile = copy(conf.profiles[0])
        newProfile.quality = 70
        assert conf.profiles[0].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 90}
        assert conf.profiles[4].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 80}
        assert 5 == conf.addprofile(newProfile)
        assert conf.profiles[0].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 90}
        assert conf.profiles[4].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 80}
        assert conf.profiles[5].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 70}

        # Create a new profile that is a copy of the first default profile
        # that has the same quality but a very large size. The name of the
        # first, fifth and sixth profiles should still be changed to contain
        # the quality, but the name of the new profile should be the default
        newProfile = copy(conf.profiles[0])
        newProfile.size = None
        newProfile.width = 2000
        newProfile.height = 2000
        newProfile.createname(setSelf=True)
        assert conf.profiles[0].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 90}
        assert conf.profiles[4].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 80}
        assert conf.profiles[5].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 70}
        assert 6 == conf.addprofile(newProfile)
        assert conf.profiles[0].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 90}
        assert conf.profiles[4].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 80}
        assert conf.profiles[5].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 70}
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
        assert conf.profiles[0].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 90}
        assert conf.profiles[4].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 80}
        assert conf.profiles[5].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 70}
        assert conf.profiles[6].createname() == conf.profiles[6].name
        assert 7 == conf.addprofile(newProfile)
        assert conf.profiles[0].name == pname % {"imageSize": _("small") + " (640x640)", "uploadUrl": up, "quality": 90}
        assert conf.profiles[4].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 80}
        assert conf.profiles[5].name == pname % {"imageSize": _("small"), "uploadUrl": up, "quality": 70}
        assert conf.profiles[6].createname() == conf.profiles[6].name
        assert conf.profiles[7].name == pname % {"imageSize": _("small") + " (639x640)", "uploadUrl": up, "quality": 90}

    def test_deleteprofile(self):
        # Make sure there is no saved profile in /tmp/nim-test.config
        if os.path.isfile(configFile):
            os.remove(configFile)
        assert False == os.path.isfile(configFile)
        conf = Config(configFile)

        # There are 5 default profiles
        assert 5 == len(conf.profiles)

        # Keep pointers to the third and fourth profiles
        p2 = conf.profiles[2]
        p3 = conf.profiles[3]
        assert True == conf.deleteprofile(2)
        # There are now 4 profiles
        assert 4 == len(conf.profiles)
        # The original third profile is not part of the list anymore
        assert p2 != conf.profiles[2]
        # The profile that's now third was originally the fourth
        assert p3 == conf.profiles[2]

        # It's not possible to delete the last profile (custom settings)
        assert False == conf.deleteprofile(3)
        # There are still 4 profiles
        assert 4 == len(conf.profiles)

    def test_defaultfileoperations(self):
        oldconfigfile = os.path.expanduser("~/.nautilus-image-manipulator.ini")
        # Make sure the file is not present to start with
        assert False == os.path.isfile(oldconfigfile)
        # "Touch" the file, i.e. make an empty file
        with file(oldconfigfile, 'a'):
            os.utime(oldconfigfile, None)
        assert True == os.path.isfile(oldconfigfile)

        # Use a file in a folder that never exists so that the code for
        # creating the default profiles is executed, and the new folder is
        # created
        dummyconfigfile = "/tmp/nim-test-dummy/file-that-never-exists.config"
        if os.path.isdir(os.path.dirname(dummyconfigfile)):
            os.rmdir(os.path.dirname(dummyconfigfile))
        assert False == os.path.isdir(os.path.dirname(dummyconfigfile))
        conf = Config(dummyconfigfile)
        # The old config file has been deleted
        assert False == os.path.isfile(oldconfigfile)
        # The folder has been created
        assert True == os.path.isdir(os.path.dirname(dummyconfigfile))
        # Leave the system clean by deleting the newly created dummy folder
        os.rmdir(os.path.dirname(dummyconfigfile))

    def test_write(self):
        # Make sure there is no saved profile in /tmp/nim-test.config
        if os.path.isfile(configFile):
            os.remove(configFile)
        assert False == os.path.isfile(configFile)
        conf = Config(configFile)

        # There are 5 default profiles
        assert 5 == len(conf.profiles)

        # The config file doesn't exist on disk
        assert False == os.path.isfile(configFile)

        # Create a profile with percent and appendstring
        newProfile = Profile(percent=50,
                             quality=90,
                             destination="append",
                             appendstring=_("resized"))
        assert 4 == conf.addprofile(newProfile)

        # Save the file to disk
        conf.write()

        # The config file now exists on disk
        assert True == os.path.isfile(configFile)

    def test_xxlast_read(self):
        # Make sure there *is* a saved profile in /tmp/nim-test.config
        assert True == os.path.isfile(configFile)
        conf = Config(configFile)

        # There are 6 profiles in the saved config file
        assert 6 == len(conf.profiles)
        assert conf.profiles[0].name == _("Send %(imageSize)s images to %(uploadUrl)s") % {"imageSize": _("small"), "uploadUrl": "1fichier.com"}
        assert _("Create %(imageSize)s images and append \"%(appendString)s\"") % {
                              "imageSize": _("%d%% resized") % 50,
                              "appendString": _("resized")} == conf.profiles[4].name
        assert _("Custom settings") == conf.profiles[5].name

        # Test with an invalid config file
        assert True == os.path.isfile(configFile)
        with open(configFile) as f:
            read_data = f.read()
            read_data = read_data.replace("[General]", "[Invalid First Section]")
        with open(configFile, 'w') as f:
            f.write(read_data)
        # This will result in the default profiles being loaded
        conf = Config(configFile)
        # There are only 5 profiles, i.e. the default profiles
        assert 5 == len(conf.profiles)

        # Test with an empty config file
        # Make sure there is no saved profile in /tmp/nim-test.config
        if os.path.isfile(configFile):
            os.remove(configFile)
        assert False == os.path.isfile(configFile)
        # "Touch" the file, i.e. make an empty file
        with file(configFile, 'a'):
            os.utime(configFile, None)
        assert True == os.path.isfile(configFile)
        # This will result in the default profiles being loaded
        conf = Config(configFile)
        # There are only 5 profiles, i.e. the default profiles
        assert 5 == len(conf.profiles)

    def test_zipfilename(self):
        """Create different upload profiles and test the zipfile's name"""
        # Clean zipname
        newProfile = Profile(percent=50,
                             quality=90,
                             destination="upload",
                             zipname="test.zip")
        assert "test.zip" == newProfile.zipname

        # Name without ".zip"
        newProfile = Profile(percent=50,
                             quality=90,
                             destination="upload",
                             zipname="test")
        assert "test.zip" == newProfile.zipname

        # Name without ".zip" (not so nice)
        newProfile = Profile(percent=50,
                             quality=90,
                             destination="upload",
                             zipname="test.zi")
        assert "test.zi.zip" == newProfile.zipname

        # Name without ".zip" (not so nice)
        newProfile = Profile(percent=50,
                             quality=90,
                             destination="upload",
                             zipname="  test.zip  ")
        assert "test.zip" == newProfile.zipname

        # Name starting with a non-alphabetic character
        newProfile = Profile(percent=50,
                             quality=90,
                             destination="upload",
                             zipname="&test.zip")
        assert "test.zip" == newProfile.zipname

        # Name starting with a non-alphabetic character
        newProfile = Profile(percent=50,
                             quality=90,
                             destination="upload",
                             zipname=",test.zip")
        assert "test.zip" == newProfile.zipname
