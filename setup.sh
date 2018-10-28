#!/bin/bash

# Create symbolic links to the wrappers in ./bin which invoke the tools within
# the virtualenv setup in this directory.

# Get real path of current file (dereferences symbolic links).
SCRIPT=$(readlink -f $0)

# Get parent directory.
DIR=$(dirname $SCRIPT)

# Get tool absolute paths.
ABS_PATH_PD=$(readlink -f "$DIR/bin/pd")
ABS_PATH_PCLI=$(readlink -f "$DIR/bin/pcli")
ABS_PATH_PSIM=$(readlink -f "$DIR/bin/psim")

# Create symbolic links in "/usr/bin/".
ln -s $ABS_PATH_PD /usr/bin/pd
ln -s $ABS_PATH_PCLI /usr/bin/pcli
ln -s $ABS_PATH_PSIM /usr/bin/psim
