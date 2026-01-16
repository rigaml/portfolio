# Creates CloudWatch Log Group for ECS service: where the service will send its logs
resource "aws_cloudwatch_log_group" "portfolio" {
  name              = "/ecs/portfolio"
  retention_in_days = 1  # Low 'retention_in_days' for cost saving
}