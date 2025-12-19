
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  s3_use_path_style = true
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

resource "aws_dynamodb_table" "agentDemoTable" {
  name         = "agentDemoTable"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "usedID"

  attribute {
    name = "usedID"
    type = "S"
  }
}