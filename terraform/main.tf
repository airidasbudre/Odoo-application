# Local variables for common tags and naming
  locals {
    common_tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }

    name_prefix = "${var.project_name}-${var.environment}"
  }

  # VPC Module
  module "vpc" {
    source = "./modules/vpc"

    vpc_cidr     = var.vpc_cidr
    project_name = var.project_name
    environment  = var.environment
    common_tags  = local.common_tags
  }

  # Security Groups Module
  module "security" {
    source = "./modules/security"

    vpc_id       = module.vpc.vpc_id
    my_ip        = var.my_ip
    project_name = var.project_name
    environment  = var.environment
    common_tags  = local.common_tags
  }

  # EC2 Instance Module
  module "ec2" {
    source = "./modules/ec2"

    ami_id              = var.ami_id
    instance_type       = var.instance_type
    key_name            = var.key_name
    subnet_id           = module.vpc.public_subnet_id
    security_group_ids  = [module.security.ec2_security_group_id]
    project_name        = var.project_name
    environment         = var.environment
    common_tags         = local.common_tags
  }