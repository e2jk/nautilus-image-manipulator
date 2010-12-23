# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010 Emilien Klein <emilien _AT_ klein _DOT_ st>
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

# Nautilus extension to launch Nautilus Image Manipulator
# Some useful resources about Nautilus extensions:
#     http://live.gnome.org/Nautilus/Development/Extensions
#     http://svn.gnome.org/viewvc/nautilus-python/trunk/examples/
#     
# Place a copy of the extension in
#     ~/.nautilus/python-extensions/
# or
#     /usr/lib/nautilus/extensions-2.0/python/

import nautilus, os, subprocess, urllib, gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class BackgroundImageExtension(nautilus.MenuProvider):
    def __init__(self):
        pass
    
    def menu_activate_cb(self, menu, images):
        args = ["nautilus-image-manipulator"]
        for ff in images:
            # Remove "file://" and unquote the filename
            args.extend(("-f", urllib.unquote(ff.get_uri()[7:])))
        retVal = subprocess.call(args)
        
    def get_file_items(self, window, files):
        images = []
        # Extract only the images from the list of selected files
        for f in files:
            if f.get_mime_type()[:6] == "image/":
                images.append(f)
        
        # Don't display this option in the menu if there is not a single image in the selection
        if not images:
            return
        
        # TODO: Update the extension's menu label and tooltip message
        item = nautilus.MenuItem('NautilusImageManipulator::resize',
                                 _("_Resize images..."),
                                 _("Resize each selected image"))
        item.connect('activate', self.menu_activate_cb, images)
        return item,

