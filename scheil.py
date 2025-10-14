import argparse
import os
import subprocess

# grab file from argparse
parser = argparse.ArgumentParser(description="Scheil")
parser.add_argument("file", help="File to compile")
args = parser.parse_args()
file = args.file

# check if the file exists
if not os.path.isfile(file):
    print(f"File {file} does not exist.")
    exit(1)

print("Compiling your program...")

# Run lexer
subprocess.run(["python", "src/lexer.py", file], check=True)
# Run parser
subprocess.run(["python", "src/parser.py", file], check=True)

# Convert .sc → .scir
scir_file = file.replace('.sc', '.scir')
if not os.path.isfile(scir_file):
    print(f"Error: {scir_file} not generated")
    exit(1)

# Call compiler.py (NASM pipeline) directly
subprocess.run(["python", "src/compiler.py", scir_file], check=True)

file = file.replace('.sc', '')

os.remove(f"{file}.ll")
os.remove(f"{file}.scir")
os.remove(f"{file}.sctk")
os.remove(f"{file}.o")

print("Compilation complete! The executable is ready.")