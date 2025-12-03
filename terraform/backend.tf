# Uncomment this after creating S3 bucket manually
  # terraform {
  #   backend "s3" {
  #     bucket         = "your-terraform-state-bucket"
  #     key            = "odoo/terraform.tfstate"
  #     region         = "us-east-1"
  #     encrypt        = true
  #     dynamodb_table = "terraform-state-lock"
  #   }
  # }