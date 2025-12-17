resource "aws_s3_bucket" "my_agent_bucket" {
  bucket = "dev-agent-bucket-1"
  acl    = "private"
}