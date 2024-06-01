#!/usr/bin/env bash

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install AWS CLI."
    exit 1
fi

# Check if a profile name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <aws-profile-name>"
    exit 1
fi

PROFILE=$1

# Export AWS credentials to environment variables
eval $(aws configure export-credentials --profile "$PROFILE" --format env)

# Check if the export was successful
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Failed to export AWS credentials. Please check your profile name."
    exit 1
fi

# Write credentials to .env file
cat <<EOL > .env
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
EOL

echo ".env file created successfully."
