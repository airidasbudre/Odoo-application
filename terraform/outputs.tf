output "vpc_id" {
    description = "ID of the VPC"
    value       = module.vpc.vpc_id
  }

  output "ec2_public_ip" {
    description = "Public IP of EC2 instance"
    value       = module.ec2.public_ip
  }

  output "ec2_instance_id" {
    description = "EC2 Instance ID"
    value       = module.ec2.instance_id
  }

  output "ssh_command" {
    description = "SSH command to connect to EC2"
    value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${module.ec2.public_ip}"
  }

  output "odoo_url" {
    description = "Odoo application URL"
    value       = "http://${module.ec2.public_ip}:8069"
  }

  output "grafana_url" {
    description = "Grafana monitoring URL"
    value       = "http://${module.ec2.public_ip}:3000"
  }