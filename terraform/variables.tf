variable "aws_region" {
    description = "AWS region to deploy resources"
    type        = string
    default     = "us-east-1"
  }

  variable "environment" {
    description = "Environment name (dev, staging, production)"
    type        = string
    default     = "production"
  }

  variable "project_name" {
    description = "Project name for resource naming"
    type        = string
    default     = "odoo"
  }

  # VPC Configuration
  variable "vpc_cidr" {
    description = "CIDR block for VPC"
    type        = string
    default     = "10.0.0.0/16"
  }

  # EC2 Configuration
  variable "instance_type" {
    description = "EC2 instance type"
    type        = string
    default     = "t3.small"
  }

  variable "ami_id" {
    description = "AMI ID for EC2 instance (Ubuntu 22.04 in us-east-1)"
    type        = string
    default     = "ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS
  }

  variable "key_name" {
    description = "SSH key pair name"
    type        = string
  }

  variable "my_ip" {
    description = "Your IP address for SSH access (CIDR format)"
    type        = string
  }
