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
# Dependencies:
# - awslocal
#
# =================================================================================== #

#!/bin/bash
set -euo pipefail

# Enable debug mode is the DEBUG env var is set to false or if DEBUG=true is passed as
# the first argument to the script.
DEBUG="${DEBUG:-false}"
if [ "$DEBUG" == "true" ] || [ "${1:-DEBUG=false}" == "DEBUG=true" ]; then set -x; fi

# Load helper vars and functions
source helpers.sh

# Check dependencies
check-deps awslocal

# Accepts the input filename as the first and only positional argument
input_file=${1-}
if [ "$input_file" == "" ]; then
  print-error "Error: The data file path should be passed as an argument. Quitting." exit
fi

# Max depth for OU nesting is 5 (AWS Organizations limit)
#
# Logic:
#
# - Split the paths in CSV format
# - Loop through each and add the path depth to an array
# - Determine the largest number in the array to get max depth

# Read data from input file into variable
ou_path_data=$(<$input_file)

ou_max_depth=5
declare -a ou_array=()

for path in $(echo $ou_path_data); do
  declare -a path_as_array=()
  IFS='/' read -r -a path_as_array <<< "$path"
done

for 
