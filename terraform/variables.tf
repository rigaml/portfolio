variable "region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"    # Proof of concept cost saving (cheaper location)
}

variable "instance_type" {
  description = "The type of EC2 instance to use"
  type        = string
  default     = "t2.micro"    # Proof of concept small instance
}

variable "ami_name" {
  description = "The name of the AMI to use for the VM: latest Debian 11 AMI"

  default = "debian-11-amd64-*"
}

variable "ami_owners" {
  description = "The name of the AMI to use for the VM: Debian AMIs provided by AWS"
  default = ["136693071363"]
}

variable "db_name" {
  description = "Postgres database name"
  default = "portfolio"
}

variable "db_user" {
  description = "Postgres database user"
  default = "portfolio_user"
}

variable "db_password" {
  description = "Postgres database password"
  sensitive = true
}

### TODO: Set value!
variable "django_secret_key" { 
  description = "Django secret key"
  sensitive = true 
}