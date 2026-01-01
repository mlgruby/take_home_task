# Real-time Pageview Data Pipeline
# Main infrastructure composition

locals {
  common_tags = {
    Environment = terraform.workspace
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}
