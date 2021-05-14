# =================================================================================== #
#
# Uses the awslocal CLI to create the initial Organization
#
# Dependencies:
# - awslocal
# =================================================================================== #

#!/bin/bash
set -euo pipefail

# Enable debug mode is the DEBUG env var is set to false or if DEBUG=true is passed as
# the first argument to the script.
DEBUG="${DEBUG:-false}"
if [ "$DEBUG" == "true" ] || [ "${1:-DEBUG=false}" == "DEBUG=true" ]; then set -x; fi

# Get relative path of script (in case executing this from another directory)
DIR=$(realpath $(dirname "$0"))

# Load helper vars and functions
source ${DIR}/helpers.sh

# Check dependencies
check_deps awslocal

print_msg "Creating organization"
# TODO: This initial call fails due to a localstack bug, but it actually creates the
# organization. Let it fail and get details via organizations:DescribeOrganization
awslocal organizations create-organization --feature-set ALL 2>/dev/null || true

print_msg "Describing organization"
org_json=$(awslocal organizations describe-organization --query 'Organization' 2>/dev/null | jq -cr)

org_id=$(echo $org_json | jq -cr '.Id')
org_arn=$(echo $org_json | jq -cr '.Arn')
org_master_account_arn=$(echo $org_json | jq -cr '.MasterAccountArn')
org_master_account_id=$(echo $org_json | jq -cr '.MasterAccountId')
org_master_account_email=$(echo $org_json | jq -cr '.MasterAccountEmail')
org_policy_types_json=$(echo $org_json | jq -cr '.PolicyTypes')

print_msg "Found organization: $org_id"

print_msg "Listing roots"
roots_json=$(awslocal organizations list-roots --query 'Roots' | jq -cr 'map(select(.Arn | contains("'"$org_id"'")))')

root_id=$(echo $roots_json | jq -cr '.[].Id')
root_arn=$(echo $roots_json | jq -cr '.[].Arn')
root_name=$(echo $roots_json | jq -cr '.[].Name')
root_policy_types_json=$(echo $roots_json | jq -cr '.[].PolicyTypes')

print_msg "Discovered root: $root_id"
