# =================================================================================== #
#
# Loop through a fixture defining the Organization's OUs as a list of paths (like a
# filesystem). Creates OUs from the root downwards.
#
# Logic:
#
# - Get a list of all OUs at the root level
# - Create root level OUs first and record their OU IDs
# - Get a list of all OUs the next level under each parent
# - Create 1st level OUs and record their OU IDs
# - Repeat process recursively until max depth is reached
#
# =================================================================================== #


#!/bin/bash
set -euo pipefail

# Enable debug mode is the DEBUG env var is set to false or if DEBUG=true is passed as
# the first argument to the script.
DEBUG="${DEBUG:-false}"
if [ "$DEBUG" == "true" ] || [ "${1:-DEBUG=false}" == "DEBUG=true" ]; then set -x; fi

# Shell colors
ERROR="\033[31m" # Red
WARN="\033[33m"  # Yellow
OK="\033[32m"    # Green
CCEND="\033[0m"  # No Color (CCEND= "Color Code End")

# Check if stdout is a terminal. If it is, disable colored output.
if ! [ -t 1 ]; then
  ERROR="\033[31m" # Red
  WARN="\033[33m"  # Yellow
  OK="\033[32m"    # Green
  CCEND="\033[0m"  # No Color (CCEND= "Color Code End")
else
  ERROR=
  WARN=
  OK=
  CCEND=
fi

# Accepts the input filename as the first and only positional argument
input_file=${1-}
if [ "$input_file" == "" ]; then
  printf "%sError: The data file path should be passed as an argument. Quitting.%s" "$ERROR" "$CCEND"
  exit 1
fi

# Determine max depth
#
# Logic:
#
# - Split the paths in CSV format
# - Loop through each and add the path depth to an array
# - Determine the largest number in the array to get max depth

# Read data from input file into variable
ou_path_data=$(<$input_file)

ou_max_depth=0
declare -a ou_array=()

for path in $(echo $ou_path_data); do
  declare -a path_as_array=()
  IFS='/' read -r -a path_as_array <<< "$path"
  ou_array+=$path_as_array
done

printf "%s%s: %d%s" "$OK" "Discovered OUs" "$CCEND"
