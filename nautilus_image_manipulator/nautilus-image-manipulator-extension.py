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

# Nautilus extension to launch Nautilus Image Manipulator.
#
# Place a copy of this extension in
#   /usr/share/nautilus-python/extensions
# or
#   ~/.local/share/nautilus-python/extensions/
#
# Some useful resources about Nautilus extensions:
#   http://projects.gnome.org/nautilus-python/
#   http://git.gnome.org/browse/nautilus-python/tree/examples
#   http://git.gnome.org/browse/nautilus-python/tree/examples?h=nautilus-3.0
#
# Note that as of nautilus-python 0.7.0 the path from where the extensions
# are loaded has been changed:
#   http://git.gnome.org/browse/nautilus-python/commit/?id=c97253104e7d6b88803cbef529bd9e298fa8d9e3
#   http://git.gnome.org/browse/nautilus-python/commit/?h=nautilus-3.0&id=73d2739c4a91d80710b14ff5f192875a34f10a94


import os
import subprocess
import urllib

import gettext
from gettext import gettext as _
from gettext import ngettext
gettext.textdomain('nautilus-image-manipulator')

from gi.repository import Nautilus, GObject


class BackgroundImageExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        pass

    def menu_activate_cb(self, menu, images):
        args = ["nautilus-image-manipulator"]
        for ff in images:
            # Remove "file://" and unquote the filename
            args.extend(("-f", urllib.unquote(ff.get_uri()[7:])))
        subprocess.Popen(args)

    def get_file_items(self, window, files):
        images = []
        # Extract only the images from the list of selected files
        for f in files:
            if f.get_mime_type()[:6] == "image/":
                images.append(f)

        # Don't display this option in the menu if there is not a single
        # image in the selection
        if not images:
            return

        extLabel = ngettext("_Resize image", "_Resize images", len(images))
        extTip = ngettext("Resize the selected image",
                          "Resize each selected image",
                          len(images))

        item = Nautilus.MenuItem(name='NautilusImageManipulator::resize',
                                 label=extLabel,
                                 tip=extTip)
        item.connect('activate', self.menu_activate_cb, images)
        return item,

