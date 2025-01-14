# Aion

## Summary

A repository containing a prototype application that separates circular objects from their background.

Users are directed to [local testing notebook](./notebooks/local_testing.ipynb) as demonstration of project output.

The notebook breaks down challenges' requirements into individual pieces before addressing them with API calls.

## Areas of Improvement

### Minimalist Circle Identification Capability

Circles in the image are identified through traditional non-machine-learning method. Such technique is reliable in a small scale but impractical in the long term with more varied input images.

### Missing Evaluation Strategy

Evaluation of algorithm output currently can only be done manually. While this is appropriate for a proof of concept. A production grade solution, if one involving machine learning, requires either annotated ground truth data or a generative model for more dynamic and probabilistic evaluation.

### Insufficient Query Capability

Querying circles and images require existing knowledge about their URIs. Certain pre-configured queries would help speed up the process to identify propoer URIs.

### Sporadic Documentation

"Self-documentation" through typing and comments is insufficient. The minimalist README makes maintainence difficult.

### Zero Test Coverage

No automated test of any kind exists.

### Incomplete Local Integration Test Harness

Docker compose is not configured to test multiple services in conjunction.

### Missing Local Only Test Harness

Local testing currently requires a remote sandbox environment on AWS. This may not be ideal for automated testing.

### Incomplete Deployment Logic

Storage instances such as S3 and DynamoDB are deployed but compute instances such as Lambda / ECS are not deployed.

A longer-term solution would be to deploy individual APIs as Lambdas before linking them together with S3 and DynamoDB with the help of EventBridge. EventBridge serves as a message broker, a central nervous system that links all components together in an infinitely scalable way.

### Minimalist Deployment

DynamoDB and S3 may not be the best deployment options for JSON and image data. More sophisticated options such as relational databases and data lakehouses (e.g. DataBrick) may be more appropriate.

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

### Start Raw Image Upload Service

```sh
uvicorn aion.nodes.upload_img_to_s3:app --reload
```

### Start Circle Parsing Service

```sh
uvicorn aion.nodes.parse_circles_and_upload:app --reload
```

### Start Circles Query By Image Service

```sh
uvicorn aion.nodes.get_circular_objs:app --reload
```

### Start Circle Query Service

```sh
uvicorn aion.nodes.get_circular_obj:app --reload
```

### Start Image Resize Service

```sh
uvicorn aion.nodes.resize_images:app --reload
```

### Start Image Query Service

```sh
uvicorn aion.nodes.request_frames:app --reload
```
