resource "aws_dynamodb_table" "agent_table" {
  name           = "AgentDemoTable"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "UserId"

  attribute {
    name = "UserId"
    type = "S" # String
  }
  
  tags = {
    Environment = "LocalStack"
  }
}