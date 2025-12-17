# IAM Role Definition for a Lambda Function
resource "aws_iam_role" "agent_lambda_exec_role" {
  name = "agent-lambda-role"
  
  # This is the rule that says: "Only the AWS Lambda service is allowed to use (assume) this security role.
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
    }],
  })
}

# IAM Policy (Permissions for CloudWatch logs)
# "agent_lambda_policy" the internal name or local name you use to reference this policy within your Terraform code
resource "aws_iam_policy" "agent_lambda_policy" {
  name        = "agent-lambda-basic-execution-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attaches the Policy to the Role
resource "aws_iam_role_policy_attachment" "agent_lambda_policy_attach" {
  role       = aws_iam_role.agent_lambda_exec_role.name
  policy_arn = aws_iam_policy.agent_lambda_policy.arn
}