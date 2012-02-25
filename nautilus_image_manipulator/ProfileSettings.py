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


import gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class Profile:
    def __init__(self, builder, name='unnamed profile', id=0, default=False, inpercent=False, width=640, 
                percent=50, quality=95, destination='append', appendstring='resized', foldername='resized',
                url='1Fichier.com', mailer='thunderbird'):
        self.builder = builder
        self.name = name
        self.id = id
        self.default = default
        self.inpercent = inpercent
        self.width = width
        self.percent = percent
        self.quality = quality
        self.destination = destination
        self.appendstring = appendstring
        self.foldername = foldername
        self.url = url
        self.mailer = mailer

    def loadfromprofile(self):
        model = self.builder.get_object("profiles_combo").get_model()
        iter = self.builder.get_object("profiles_combo").get_active_iter()
        self.name = model.get_value(iter, 0)
        self.id = model.get_value(iter, 1)
        self.default = model.get_value(iter, 2)
        self.inpercent = model.get_value(iter, 3)
        self.width = model.get_value(iter, 4)
        self.percent = model.get_value(iter, 6)
        self.quality = model.get_value(iter, 7)
        self.destination = model.get_value(iter, 8)
        self.appendstring = model.get_value(iter, 9)
        self.foldername = model.get_value(iter, 10)
        self.url = model.get_value(iter, 11)
        self.mailer = model.get_value(iter, 12)
        
    def loadfromui(self):
        self.inpercent = self.builder.get_object("percent_radio").get_active()
        self.width = self.builder.get_object("width_spin").get_value()
        self.percent = self.builder.get_object("percent_scale").get_value()
        self.quality = self.builder.get_object("quality_scale").get_value()
        iter = self.builder.get_object("destination_combo").get_active_iter()
        self.destination = self.builder.get_object("destination_combo").get_model().get_value(iter, 1)
        self.builder.get_object("width_spin").get_text()        
        self.appendstring = self.builder.get_object("append_entry").get_text()
        self.foldername = self.builder.get_object("subfolder_entry").get_text()
        iter = self.builder.get_object("upload_combo").get_active_iter()
        self.url = self.builder.get_object("upload_combo").get_model().get_value(iter, 0)
        iter = self.builder.get_object("mailer_combo").get_active_iter()
        self.mailer = self.builder.get_object("mailer_combo").get_model().get_value(iter, 0)
