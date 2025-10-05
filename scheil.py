'''
Scheil main executable
Copyright (c) 2025-2026 Webbrowser11
MIT License
'''
import argparse
import os
import subprocess
# grab file from argparse
argparser = argparse.ArgumentParser(description="Scheil lexer")
argparser.add_argument("file", help="File to lex")
args = argparser.parse_args()
file = args.file
file = rf"{file}" # avoid raw file mixups and stuff.
# run lexer
# check if the file exists, so i "don't repeat myself."
if not os.path.isfile(file):
    print(f"File {file} does not exist.")
    exit(1)
print("Compiling your program...")
subprocess.run(["python3", "src/lexer.py", file])
subprocess.run(["python3", "src/parser.py", file])
subprocess.run(["python3", "src/compiler.py", file])
# cleanup
file = file[:-3]
os.remove(f"{file}.sctk")
os.remove(f"{file}.scir")
print(f"Done! Your output file is {file}.sc")