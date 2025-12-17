import subprocess
import os

class TerraformExecutor:
    def __init__(self, terraform_dir="Terraform"):
        self.terraform_dir = terraform_dir

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
        # 1. Write the code to the main.tf file
        tf_file_path = os.path.join(self.terraform_dir, "main.tf")
        with open(tf_file_path, "w") as f:
            f.write(tf_code)

        # 2. Run Init (in case new providers are needed)
        init_res = self.run_command("terraform init")
        if "Error" in init_res:
            return init_res

        # 3. Run Apply
        apply_res = self.run_command("terraform apply -auto-approve")
        return apply_res

    def destroy_infrastructure(self):
        """Destroys the managed infrastructure."""
        return self.run_command("terraform destroy -auto-approve")