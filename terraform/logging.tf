# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "portfolio" {
  name              = "/ecs/portfolio"
  retention_in_days = 3  # Low 'retention_in_days' for cost saving
}

# IAM role for ECS tasks to write logs
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "portfolio-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Policy to allow writing to CloudWatch Logs
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}