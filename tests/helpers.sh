# =================================================================================== #
#
# Helper functions and aliases for the rest of the scripts. This is intended to be
# sourced from the calling script or shell.
#
# =================================================================================== #

#!/bin/bash

# Handle shell color codes

# Check if stdout is a terminal. If it is, disable colored output.
if [ -t 1 ]; then
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

export OK=$OK
export WARN=$WARN
export ERROR=$ERROR
export CCEND=$CCEND

# Alias function to shorten typing
function awsorgs() {
  aws organizations $@
}

# Takes a string and prints a colored error message with a newline. Optionally allows
# exiting with a default or custom error code.
#
# Usage: print_error <string to print> [exit|noexit] [errcode]
#
# Examples:
# - print_error "This prints but does not cause the script to exit"
# - print_error "This prints and then exits with with error code of 1" exit
# - print_error "This prints and then exits with a custom error code" exit 255
function print_error() {
  err_msg=$1
  err_exit_arg=${2:-noexit}
  err_code=${3:-1}
  err_exit=false
  printf "${ERROR}%s${CCEND}\n" "$err_msg" >&2
  if [ "$err_exit_arg" == "exit" ]; then exit $err_code; fi
}

# Takes a string and prints a colored message with a newline
function print_msg() {
  msg=${1-}
  printf "${OK}%s${CCEND}\n" "$msg" >&2
}

# Function to check that dependencies are installed
# Usage: check-binary-deps <list of binary commands>
function check_deps() {
  deps=$@
  deps_not_found=
  for dep in $deps; do
    if ! command -v $dep &> /dev/null; then deps_not_found+="$dep "; fi
  done

  if [ "$deps_not_found" != "" ]; then
    print_error "This script has unmet dependencies: $deps_not_found" exit
  fi
}

# Function to list children for a parent id.
# Usage: list-children <accounts|ous> <parent-id> <parent-name>
function list_children() {
  # Variables
  api_action=
  child_type=${1:-}
  parent_id=${2:-}
  parent_name=${3:-}
  query_string=

  # First arg is "accounts" or "ous"
  case $child_type in
    accounts)
      api_action="list-accounts-for-parent"
      query_string="Accounts"
      ;;
    ous)
      api_action="list-organizational-units-for-parent"
      query_string="OrganizationalUnits"
      ;;
    *)
      return 1 
      ;;
  esac

  # Get the children for the parent
  # Add a ParentId and ParentName field to each object
  json_data=$(awsorgs $api_action                         \
                      --parent-id $parent_id              \
                      --query $query_string               \
                      --output json                       \
                      2>/dev/null                         \
                      |                                   \
                      jq -crM                             \
                         --arg parent_id $parent_id       \
                         --arg parent_name "$parent_name" \
                         '[.[] | . + {ParentId: $parent_id, ParentName: $parent_name}]')

  echo $json_data | jq -crM
}
