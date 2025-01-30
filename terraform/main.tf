provider "aws" {
  region = var.region
}

# Fetch available AZs dynamically for the specified region
data "aws_availability_zones" "available" {}

# VPC and Network Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "portfolio-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = [data.aws_availability_zones.available.names[0]]  # Proof of concept - only one AZ
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
  single_nat_gateway = true  # Proof of concept - cost saving
}

# EC2 Instance for PostgreSQL
resource "aws_instance" "db" {
  ami           = "ami-04b4f1a9cf54c11d0"  # Ubuntu 24.04 ("DeprecationTime": "2027-01-15T09:17:20.000Z")
  instance_type = var.instance_type
  
  subnet_id     = module.vpc.private_subnets[0]
  vpc_security_group_ids = [aws_security_group.db.id]
  
  root_block_device {
    volume_size = 20
  }
  
  tags = {
    Name = "portfolio-db"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "portfolio-cluster"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "portfolio-app"
  network_mode            = "awsvpc"
  requires_compatibilities = ["EC2"]
  cpu                     = "256"
  memory                  = "512"
  
  container_definitions = jsonencode([
    {
      name      = "portfolio-app"
      image     = "${aws_ecr_repository.app.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        {
          name  = "DJANGO_SETTINGS_MODULE"
          value = "portfolio.settings_prod"
        },
        {
          name  = "DB_HOST"
          value = aws_instance.db.private_ip
        }
      ]
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "portfolio-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1  # Low instance count for cost saving
  
  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.app.id]
  }
}