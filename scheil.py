'''
Scheil main executable
Copyright (c) 2025-2026 Webbrowser11
MIT License
'''
import argparse
import os
import subprocess
# grab file from argparse
argparser = argparse.ArgumentParser(description="Scheil")
argparser.add_argument("file", help="File to compile")
args = argparser.parse_args()
file = args.file
file = rf"{file}" # avoid raw file mixups and stuff.
# run lexer
# check if the file exists, so i "don't repeat myself."
if not os.path.isfile(file):
    print(f"File {file} does not exist.")
    exit(1)
print("Compiling your program...")
subprocess.run(["python", "src/lexer.py", file])
subprocess.run(["python", "src/parser.py", file])
# Convert .sc to .scir for the compiler
scir_file = file.replace('.sc', '.scir')
subprocess.run(["python", "src/compiler.py", scir_file, "--direct"])
# cleanup
file = file[:-3]
os.remove(f"{file}.sctk")
os.remove(f"{file}.scir")
os.remove(f"{file}.ll")
os.remove(f"{file}.s")