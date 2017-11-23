#!/bin/sh

# this is the package we are adding or changing version of
PACKAGE_MACRO='MOTOR'

# path to package - need to escape any $ in this path
PACKAGE_PATH='\$(SUPPORT)/motor/R6-9'

# this is only used for adding a new package
PACKAGE_AFTER='ZLIB'

## this changes the version of a package
find . -name RELEASE -exec sed -i -e "s%^${PACKAGE_MACRO}[ ]*=.*%${PACKAGE_MACRO}=${PACKAGE_PATH}%" {} \;

## this adds a new package
#find . -name RELEASE -exec sed -i -e "s%^${PACKAGE_AFTER}[ ]*=%${PACKAGE_MACRO}=${PACKAGE_PATH}\n${PACKAGE_AFTER}=%" {} \;
