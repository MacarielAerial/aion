# Blob storage for images
resource "aws_s3_bucket" "aion_bucket" {
  bucket         = "aion-dev-34567"

  tags           = {
    Name         = "RawImageBucket"
  }
}

# NoSQL for JSON data
resource "aws_dynamodb_table" "circular_objs_table" {
  name           = "CircularObjsTable"
  billing_mode   = "PAY_PER_REQUEST"

  hash_key       = "uri_image"

  attribute {
    name = "uri_image"
    type = "S"

  }

  tags           = {
    Name         = "CircularObjsDynamoDBTable"
  }
}
