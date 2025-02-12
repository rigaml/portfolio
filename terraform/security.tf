# Security Group: defines the rules for inbound/outbound traffic

# Security Group for Database
resource "aws_security_group" "db" {
  name        = "portfolio-db-sg"
  description = "Security group for PostgreSQL database"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }
}

# Security Group for App
resource "aws_security_group" "app" {
  name        = "portfolio-app-sg"
  description = "Security group for application"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
