output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.odoo.id
}

output "public_ip" {
  description = "Public IP address (Elastic IP)"
  value       = aws_eip.odoo.public_ip
}

output "private_ip" {
  description = "Private IP address"
  value       = aws_instance.odoo.private_ip
}

output "instance_state" {
  description = "State of the instance"
  value       = aws_instance.odoo.instance_state
}
