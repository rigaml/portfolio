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
  description = "The name of the AMI to use for the VM, default is the latest Debian 11 AMI"

  default = "debian-11-amd64-*"
}

variable "ami_owners" {
  description = "The owners of the AMI to use for the VM, default is the official Debian AMI"

  default = ["136693071363"]   #Amazon owner
}
