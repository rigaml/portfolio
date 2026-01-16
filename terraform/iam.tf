# IAM Role for ECS Instances
resource "aws_iam_role" "ecs" {
  name = "ecs-instance-role"
  
  # Trust relationship policy that allows EC2 to assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Allows permissions to manage EC2 instances within your ECS cluster.
resource "aws_iam_role_policy_attachment" "ecs_service" {
  role       = aws_iam_role.ecs.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

# Allows to write to CloudWatch logs
resource "aws_iam_role_policy_attachment" "ecs_cloudwatch" {
  role       = aws_iam_role.ecs.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# Allows pulling images from ECR
resource "aws_iam_role_policy_attachment" "ecs_ecr" {
  role       = aws_iam_role.ecs.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECR-ReadOnly"
}

# Create an instance profile that attaches to EC2 instances
resource "aws_iam_instance_profile" "ecs" {
  name = "ecs-instance-profile"
  role = aws_iam_role.ecs.name
}

# Creates IAM role for ECS tasks to write logs
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "portfolio-ecs-task-execution-role"

  # Allows an ECS service to assume this role
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

# Allows ECS tasks to write to CloudWatch Logs
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}