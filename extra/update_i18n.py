#!/usr/bin/python
# Copyright (C) 2010-2011 Emilien Klein <emilien _AT_ klein _DOT_ st>
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

import os
import shutil

def main():
    poFolder = "./po"
    # Check if the folder exists, i.e. uiFolder is a valid folder
    if not os.path.isdir(poFolder):
        # The folder does not exist, we are probably not running the script from the root of the repository
        # Exit with an error message
        print "ERROR: Please run this script from the root of the repository."
        exit(-1)
    
    # Temporarily rename the nautilus extension so that it gets analyzed for translations
    os.rename("nautilus_image_manipulator/nautilus-image-manipulator-extension.py",
              "nautilus_image_manipulator/nautilus-extension.py")
    
    # Run build_i18n
    os.system("python setup.py build_i18n")
    
    # Rename the extension back to it's original name
    os.rename("nautilus_image_manipulator/nautilus-extension.py",
              "nautilus_image_manipulator/nautilus-image-manipulator-extension.py")
    
    # Delete the "./build" directory that got created
    shutil.rmtree("./build")

if __name__ == '__main__':
    main()
