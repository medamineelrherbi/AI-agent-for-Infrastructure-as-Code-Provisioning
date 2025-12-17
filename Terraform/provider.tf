terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  # Use the mock credentials set in docker-compose
  access_key = "test"
  secret_key = "test"
  region     = "us-east-1"
  s3_use_path_style = true

  # Crucial: Point the AWS provider to the LocalStack endpoint
  # You can use the `tflocal` wrapper for this automatically, 
  # but showing the manual way first is helpful.
  endpoints {
    s3 = "http://localhost:4566"
  }

  # These flags skip AWS metadata checks that would fail locally
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

/* 
The provider.tf File: This file tells Terraform how to communicate with the cloud provider (in your case, the LocalStack API).
 It must be present in the directory where you run terraform init and terraform apply.
*/