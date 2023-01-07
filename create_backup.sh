#!/bin/bash - 
#===============================================================================
#
#          FILE: create_backup.sh
# 
#         USAGE: ./create_backup.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 29.12.2022 22:24
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error
set -o errexit

path_script='/home/konkov/Documents/scripts/backup_ws/'

source "${path_script}venv/bin/activate"
python3 $path_script'backup.py'
deactivate
