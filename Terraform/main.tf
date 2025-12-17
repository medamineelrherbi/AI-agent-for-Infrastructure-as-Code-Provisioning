
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    s3       = "http://localhost:4566"
    sqs      = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
    iam      = "http://localhost:4566"
  }
}

resource "aws_sqs_queue" "test_queue" {
  name                      = "test-queue-react"
  visibility_timeout_seconds = 60
  
  tags = {
    Name = "test-queue-react"
  }
}