terraform {
  backend "s3" {
    bucket         = "odoo-terraform-state-723977204493"
    key            = "odoo/terraform.tfstate"
    region         = "eu-north-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
