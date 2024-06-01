resource "aws_s3_bucket_acl" "aion_bucket" {
  bucket = "aion-dev-34567"
  acl    = "private"
}