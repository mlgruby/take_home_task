# Real-time Pageview Data Pipeline
# LocalStack environment configuration

terraform {
  # Local backend for development
  backend "local" { # This can be changed to remote backend for production on S3 or other cloud storage
    path = "terraform.tfstate"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.27.0"
    }
  }

  required_version = ">= 1.14.3"
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  # LocalStack endpoints (S3 and IAM only)
  endpoints {
    s3         = var.localstack_endpoint
    iam        = var.localstack_endpoint
    sts        = var.localstack_endpoint
    cloudwatch = var.localstack_endpoint
    logs       = var.localstack_endpoint
    # Kafka and Kinesis endpoints removed (native services used)
  }

  # Default tags for all resources
  default_tags {
    tags = local.common_tags
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
