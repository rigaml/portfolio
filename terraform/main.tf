terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.84.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Defines the Amazon Machine Image to use
data "aws_ami" "debian" {
  most_recent = true  
  owners      = var.ami_owners

  filter {
    name   = "name"
    values = [var.ami_name]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block       = "10.0.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name = "main"
  }
}

# Public Subnet for the API
resource "aws_subnet" "public_api" {
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 4, 1)
  vpc_id            = aws_vpc.main.id   # Associates the subnet with the VPC.
  availability_zone = "${var.region}a"  # Specifies the AWS availability zone - Proof of concept cost saving only one zone
}

# Private Subnet for Database
resource "aws_subnet" "private_db" {
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 4, 2)
  vpc_id            = aws_vpc.main.id
  availability_zone = "${var.region}a" # Specifies the AWS availability zone - Proof of concept cost saving only one zone
}

# EC2 Instance for PostgreSQL Database (instead of RDS using an EC2 instance as it is cheaper)
resource "aws_instance" "db" {
  ami           = data.aws_ami.debian.id
  instance_type = var.instance_type
  
  subnet_id     = aws_subnet.private_db.id
  vpc_security_group_ids = [aws_security_group.db.id]
  
  root_block_device {
    volume_size = 20   # Size of the storage volume in GB
    encrypted   = true  # Enable encryption for the root volume (will use the default KMS key)
  }
  
  tags = {
    Name = "portfolio-db"
  }
}

# Creates the Elastic Container Registry (ECR) repository.
resource "aws_ecr_repository" "app" {
  name = "portfolio-app"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "portfolio-cluster"
}

# Add an Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}

# Create a public route table
resource "aws_route_table" "public_api" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

# Associate public subnet with the route table
resource "aws_route_table_association" "public_api" {
  subnet_id      = aws_subnet.public_api.id
  route_table_id = aws_route_table.public_api.id
}

# ECS Task Definition: runs the Docker container for the application
resource "aws_ecs_task_definition" "app" {
  family                  = "portfolio-app"
  network_mode            = "awsvpc"
  requires_compatibilities= ["EC2"]  # Specifies application will run on EC2
  cpu                     = "256"
  memory                  = "512"
  
  container_definitions = jsonencode([
    {
      name      = "portfolio-app"
      image     = "${aws_ecr_repository.app.repository_url}:latest"  # Pulls the latest image for the application from ECR - images created during GitHub CI/CD
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
          value = aws_instance.db.private_ip   # Uses the private IP address of the EC2 instance to connect to the database
        }
      ]

      # Specifies the logging configuration
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.portfolio.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }      
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
    subnets         = [aws_subnet.public_api.id]
    security_groups = [aws_security_group.app.id]
  }
}