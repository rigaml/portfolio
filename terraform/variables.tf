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