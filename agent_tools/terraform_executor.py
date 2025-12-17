import subprocess
import os
import re

class TerraformExecutor:
    def __init__(self, terraform_dir="Terraform"):
        self.terraform_dir = terraform_dir
        if not os.path.exists(self.terraform_dir):
            os.makedirs(self.terraform_dir)
        self.provider_content = """
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  s3_use_path_style = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    s3       = "http://localhost:4566"
    sqs      = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
    iam      = "http://localhost:4566"
  }
}
"""

    def run_command(self, command):
        """Helper to run shell commands in the Terraform directory."""
        try:
            result = subprocess.run(
                command,
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                return f"Success:\n{result.stdout}"
            else:
                return f"Error:\n{result.stderr}"
        except Exception as e:
            return f"Exception occurred: {str(e)}"

    def apply_infrastructure(self, tf_code: str):
        """Writes code to main.tf and applies it."""

        # SAFETY: Remove 'provider "aws" {...}' if the LLM hallucinated it
        # This regex looks for provider "aws" block and removes it
        clean_code = re.sub(r'provider\s+"aws"\s+\{[^{}]*(\{[^{}]*\}[^{}]*)*\}','',tf_code,flags=re.DOTALL)


        # 1. Write the code to the main.tf file
        tf_file_path = os.path.join(self.terraform_dir, "main.tf")
        full_config = self.provider_content + "\n" + clean_code
        
        with open(tf_file_path, "w") as f:
            f.write(full_config)

        # 2. Run Init
        init_res = self.run_command("terraform init")
        if "Error" in init_res:
            return init_res

        # 3. Run Apply
        # Note: Llama 3 often provides Markdown blocks (```hcl), strip them if present
        return self.run_command("terraform apply -auto-approve")

    def destroy_infrastructure(self):
        """Destroys the managed infrastructure."""
        return self.run_command("terraform destroy -auto-approve")