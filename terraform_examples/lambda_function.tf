resource "aws_lambda_function" "agent_lambda" {
  function_name    = "agent-hello-lambda"
  
  # Placeholder file name - you need to zip your code and place it in the agent_output folder
  filename         = "function.zip" 
  
  handler          = "index.handler" 
  runtime          = "nodejs18.x" 
  timeout          = 60
  memory_size      = 128

  # Crucial: Must reference the ARN of the IAM role
  role             = aws_iam_role.agent_lambda_exec_role.arn
  
  # The agent must compute this hash based on the file contents
  source_code_hash = filebase64sha256("function.zip")
  
  tags = {
    Purpose = "Testing"
  }
}