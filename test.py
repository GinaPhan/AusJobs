import os

folder_name = "financial_data_output_backup"
folder_path = os.path.join(os.getcwd(), folder_name)
file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])

print(f"Number of files in {folder_name}: {file_count}")