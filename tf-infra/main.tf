# Blob storage for images with circles
resource "aws_s3_bucket" "aion_circle_bucket" {
  bucket         = "aion-circle-dev-34567"
  force_destroy  = true

  tags           = {
    Name         = "RawImageBucket"
  }
}

# NoSQL for circle's JSON data
resource "aws_dynamodb_table" "circular_objs_table" {
  name           = "CircularObjsTable"
  billing_mode   = "PAY_PER_REQUEST"

  hash_key       = "uri_circle"

  attribute {
    name = "uri_circle"
    type = "S"

  }

  attribute {
    name = "uri_image"
    type = "S"

  }

  global_secondary_index {
    name            = "UriImageIndex"
    hash_key        = "uri_image"
    projection_type = "ALL"
  }

  tags           = {
    Name         = "CircularObjsDynamoDBTable"
  }
}

# NoSQL for resized image data
resource "aws_dynamodb_table" "resized_frames_table" {
  name           = "ResizedFramesTable"
  billing_mode   = "PAY_PER_REQUEST"

  hash_key       = "frame_id"

  attribute {
    name = "frame_id"
    type = "N"

  }

  tags           = {
    Name         = "ResizedFramesDynamoDBTable"
  }
}