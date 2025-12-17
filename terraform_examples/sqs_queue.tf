resource "aws_sqs_queue" "agent_queue" {
  name                      = "agent-demo-queue"
  delay_seconds             = 0
  message_retention_seconds = 345600 # 4 days
  visibility_timeout_seconds = 30 # Default
  
  tags = {
    Name = "AgentSQSQueue"
  }
}