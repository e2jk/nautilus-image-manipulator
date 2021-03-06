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
import sys

try:
    import DistUtilsExtra.auto
except ImportError:
    print >> sys.stderr, 'To build nautilus-image-manipulator you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)
assert DistUtilsExtra.auto.__version__ >= '2.18', 'needs DistUtilsExtra.auto >= 2.18'

def update_data_path(prefix, oldvalue=None):

    try:
        fin = file('nautilus_image_manipulator/nautilus_image_manipulatorconfig.py', 'r')
        fout = file(fin.name + '.new', 'w')

        for line in fin:
            fields = line.split(' = ') # Separate variable from value
            if fields[0] == '__nautilus_image_manipulator_data_directory__':
                # update to prefix, store oldvalue
                if not oldvalue:
                    oldvalue = fields[1]
                    line = "%s = '%s'\n" % (fields[0], prefix)
                else: # restore oldvalue
                    line = "%s = %s" % (fields[0], oldvalue)
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find nautilus_image_manipulator/nautilus_image_manipulatorconfig.py")
        sys.exit(1)
    return oldvalue


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        previous_value = update_data_path(self.prefix + '/share/nautilus-image-manipulator/')
        DistUtilsExtra.auto.install_auto.run(self)
        update_data_path(self.prefix, previous_value)


def nautilus_plugin():
    files = []
    files.append(('share/nautilus-python/extensions', ['nautilus_image_manipulator/nautilus-image-manipulator-extension.py']))
    return files

DistUtilsExtra.auto.setup(
    name='nautilus-image-manipulator',
    version='1.3',
    license='GPL-3',
    author='Emilien Klein',
    author_email='emilien _AT_ klein _DOT_ st',
    description='Resize and send images from Nautilus',
    long_description="""This Nautilus extension lets you resize images and send them to friends
and family, right from Nautilus.

Just right-click on any photo or group of photos, and an option will
appear that launches Nautilus Image Manipulator.

A set of default settings make it easy to quickly resize pictures. You
can also easily create your own profiles for later reuse.""",
    url='https://launchpad.net/nautilus-image-manipulator',
    packages=["nautilus_image_manipulator", "nautilus_image_manipulator.upload", "nautilus_image_manipulator.upload.poster"],
    data_files=nautilus_plugin(),
    cmdclass={'install': InstallAndUpdateDataDirectory}
    )

