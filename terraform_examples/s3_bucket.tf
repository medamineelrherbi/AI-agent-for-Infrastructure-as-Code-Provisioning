resource "aws_s3_bucket" "my_agent_bucket" {
  bucket = "agent-created-bucket-example"
  acl    = "private"
  tags = {
    Environment = "LocalStack"
    Project     = "AI_Agent_Demo"
  }
}