"""
Contactenates the specified `file_paths` for later use as input in a LLM

LLM prompt:
Please act as an experienced and helpful professional developer with experience deploying Django APIs to Aws using GitHub Actions, Docker, Terraform.
I build a Django API and want to deploy it to AWS using GitHub Actions, Docker, Terraform. 
Review the below files and make sure are correct and when API is deployed it will work. 
Before presenting your response, carefully review it and ensure it is correct, well-designed, maintainable, functional and aligned with best practices.
"""
def concatenate_files(file_paths, output_file):
    try:
        with open(output_file, 'w') as outfile:
            for file_path in file_paths:
                try:
                    with open(file_path, 'r') as infile:
                        # Write the file path as a header
                        outfile.write(f"=== File: {file_path} ===\n")
                        # Write the content of the file
                        outfile.write(infile.read())
                        # Add a separator between files
                        outfile.write("\n\n")
                except FileNotFoundError:
                    print(f"Warning: File '{file_path}' not found. Skipping.")
                except IOError as e:
                    print(f"Error reading file '{file_path}': {e}")
        print(f"Successfully concatenated files into '{output_file}'.")
    except IOError as e:
        print(f"Error writing to output file '{output_file}': {e}")


file_paths = [
'terraform/variables.tf',
'terraform/main.tf',
'terraform/security.tf',
'terraform/iam.tf',
'terraform/logging.tf',
'terraform/output.tf',
'docker-compose.development.yml',
'docker-compose.production.yml',
'docker-compose.local.yml',
'.github/workflows/deploy.yml',
'Dockerfile.production',
'portfolio/settings/base.py',
'portfolio/settings/development.py',
'portfolio/settings/production.py'
]

output_file = 'concatenated_output.txt'
concatenate_files(file_paths, output_file)