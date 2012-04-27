#!/bin/bash
rm -rf ./cover && nosetests --with-coverage --cover-html --cover-package=nautilus_image_manipulator --cover-inclusive
