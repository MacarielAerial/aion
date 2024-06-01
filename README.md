# Aion

## Summary

A repository containing a prototype application that separates circular objects from their background.

## Areas of Improvement

### Infrastructure Code Sitting Next to Application Code

Tightly coupled infrastructure and application logic can be beneficial especially for microservice architecture with largely mutually exclusive infrastructure requirement. Nonetheless, the strength can easily become a major weakness if multiple projects share the same infrastructure (e.g. the same S3 bucket to serve as a data lake).

## Code Snippets

### Configure and Login with Developer Profile

```sh
# Configure a profile first
aws sso configure
# Log into an example profile after configuration
aws sso login --profile malcador
```

### Export AWS Credentials as Environmental Variables Into a .env File

```sh
./scripts/save_aws_credentials.sh  malcador
```
