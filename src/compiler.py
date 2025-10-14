"""
Scheil Compiler
Copyright (c) 2025-2026
MIT License
"""

import os
import argparse
import subprocess
import sys

def compile_scir_to_llvm(scir_file):
    """Convert .scir IR to LLVM IR"""
    llvm_file = scir_file.replace('.scir', '.ll')
    
    with open(scir_file, 'r') as f:
        scir_content = f.read().strip()
    
    if not scir_content.startswith('output '):
        print(f"Error: Expected 'output' statement in {scir_file}")
        return None

    output_text = scir_content[7:]  # Remove 'output ' prefix
    llvm_ir = generate_llvm_ir(output_text)

    with open(llvm_file, 'w') as f:
        f.write(llvm_ir)

    return llvm_file

def generate_llvm_ir(output_text):
    """Generate LLVM IR for the output statement"""
    escaped_text = escape_string_for_llvm(output_text)
    llvm_ir = f"""; ModuleID = 'scheil'
source_filename = "scheil.scir"
target triple = "x86_64-pc-windows-gnu"

@.str = private unnamed_addr constant [{len(output_text)+1} x i8] c"{escaped_text}\\00"

declare i32 @printf(i8*, ...)

define i32 @main() {{
entry:
  %call = call i32 (i8*, ...) @printf(
      i8* getelementptr inbounds ([{len(output_text)+1} x i8],
      [{len(output_text)+1} x i8]* @.str, i64 0, i64 0))
  ret i32 0
}}
"""
    return llvm_ir

def escape_string_for_llvm(text):
    """Escape string for LLVM IR format"""
    escaped = ""
    for c in text:
        if c == '\\':
            escaped += "\\5C"
        elif c == '"':
            escaped += "\\22"
        elif c == '\n':
            escaped += "\\0A"
        elif c == '\r':
            escaped += "\\0D"
        elif c == '\t':
            escaped += "\\09"
        elif ord(c) < 32 or ord(c) > 126:
            escaped += f"\\{ord(c):02X}"
        else:
            escaped += c
    return escaped

def compile_llvm_to_object(llvm_file):
    """Compile LLVM IR to object (.o) using llc"""
    obj_file = llvm_file.replace('.ll', '.o')
    try:
        subprocess.run(['llc', '-filetype=obj', '-o', obj_file, llvm_file],
                       check=True)
        print(f"Generated object file: {obj_file}")
        return obj_file
    except subprocess.CalledProcessError as e:
        print("Error: llc failed\n", e)
        return None
    except FileNotFoundError:
        print("Error: llc not found. Install LLVM tools.")
        return None

def link_object_to_exe(obj_file):
    """Link object file to exe using gcc"""
    exe_file = obj_file.replace('.o', '.exe')
    try:
        subprocess.run(['gcc', obj_file, '-o', exe_file], check=True)
        print(f"Linked executable: {exe_file}")
        return exe_file
    except subprocess.CalledProcessError as e:
        print("Error: gcc linking failed\n", e)
        return None
    except FileNotFoundError:
        print("Error: gcc not found. Install GCC.")
        return None

def main():
    parser = argparse.ArgumentParser(description="Scheil Compiler - .scir → exe using NASM-compatible pipeline")
    parser.add_argument("file", help="Input .scir file")
    args = parser.parse_args()

    if not args.file.endswith('.scir'):
        print("Error: Input file must have .scir extension")
        sys.exit(1)
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found")
        sys.exit(1)

    llvm_file = compile_scir_to_llvm(args.file)
    if not llvm_file:
        sys.exit(1)

    obj_file = compile_llvm_to_object(llvm_file)
    if not obj_file:
        sys.exit(1)

    exe_file = link_object_to_exe(obj_file)
    if not exe_file:
        sys.exit(1)

if __name__ == "__main__":
    main()
