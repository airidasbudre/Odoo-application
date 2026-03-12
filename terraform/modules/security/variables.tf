variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "my_ip" {
  description = "Your IP address for SSH and monitoring access (CIDR format)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
