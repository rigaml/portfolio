# After creating the database instance can obtain the Ip
output "db_host" {
  description = "Private IP of the database instance"
  value       = aws_instance.db.private_ip
}