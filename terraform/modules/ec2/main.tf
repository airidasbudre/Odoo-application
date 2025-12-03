# EC2 Instance for Odoo
resource "aws_instance" "odoo" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = var.subnet_id
  vpc_security_group_ids = var.security_group_ids

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true

    tags = merge(
      var.common_tags,
      {
        Name = "${var.project_name}-${var.environment}-root-volume"
      }
    )
  }

  user_data = <<-EOF
              #!/bin/bash
              set -e

              # Update system
              apt-get update
              apt-get upgrade -y

              # Install Docker
              curl -fsSL https://get.docker.com -o get-docker.sh
              sh get-docker.sh

              # Install Docker Compose
              apt-get install -y docker-compose-plugin

              # Add ubuntu user to docker group
              usermod -aG docker ubuntu

              # Enable Docker service
              systemctl enable docker
              systemctl start docker

              # Create directory for application
              mkdir -p /home/ubuntu/odoo
              chown -R ubuntu:ubuntu /home/ubuntu/odoo

              echo "Docker installation completed" > /var/log/user-data.log
              EOF

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-ec2"
    }
  )

  lifecycle {
    ignore_changes = [
      user_data,
      ami
    ]
  }
}

# Elastic IP for EC2 instance
resource "aws_eip" "odoo" {
  instance = aws_instance.odoo.id
  domain   = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-eip"
    }
  )

  depends_on = [aws_instance.odoo]
}
