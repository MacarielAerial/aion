#!/usr/bin/env bash

# Parse named arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --profile=*)
      AWS_PROFILE="${1#*=}"
      ;;
    *)
      echo "Usage: $0 --profile=<profile_name>"
      exit 1
  esac
  shift
done

# Check if the profile name is set
if [ -z "$AWS_PROFILE" ]; then
  echo "Usage: $0 --profile=<profile_name>"
  exit 1
fi

# Select profile
export AWS_PROFILE
echo "Set aws profile to $AWS_PROFILE"

# Use the AWS CLI to get temporary credentials and export them
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile $AWS_PROFILE)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile $AWS_PROFILE)
export AWS_SESSION_TOKEN=$(aws configure get aws_session_token --profile $AWS_PROFILE)
echo "Set access key id, secret access key and session token based on cached credentials"
