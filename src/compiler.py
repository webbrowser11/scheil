"""
Scheil Compiler
Copyright (c) 2025-2026 Webbrowser11
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
    
    # Parse the output statement
    if scir_content.startswith('output '):
        output_text = scir_content[7:]  # Remove 'output ' prefix
        
        # Generate LLVM IR
        llvm_ir = generate_llvm_ir(output_text)
        
        # Write LLVM IR to file
        with open(llvm_file, 'w') as f:
            f.write(llvm_ir)
        
        print(f"Generated LLVM IR: {llvm_file}")
        return llvm_file
    else:
        print(f"Error: Expected 'output' statement in {scir_file}")
        return None

def generate_llvm_ir(output_text):
    """Generate LLVM IR for the output statement"""
    # Escape the string for LLVM IR
    escaped_text = escape_string_for_llvm(output_text)
    
    llvm_ir = f"""; ModuleID = 'scheil'
source_filename = "scheil.scir"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [{len(output_text) + 1} x i8] c"{escaped_text}\\00"

declare i32 @printf(i8*, ...)

define i32 @main() {{
entry:
  %call = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([{len(output_text) + 1} x i8], [{len(output_text) + 1} x i8]* @.str, i64 0, i64 0))
  ret i32 0
}}
"""
    return llvm_ir

def escape_string_for_llvm(text):
    """Escape string for LLVM IR format"""
    escaped = ""
    for char in text:
        if char == '\\':
            escaped += "\\5C"
        elif char == '"':
            escaped += "\\22"
        elif char == '\n':
            escaped += "\\0A"
        elif char == '\r':
            escaped += "\\0D"
        elif char == '\t':
            escaped += "\\09"
        elif ord(char) < 32 or ord(char) > 126:
            escaped += f"\\{ord(char):02X}"
        else:
            escaped += char
    return escaped

def compile_llvm_to_assembly(llvm_file):
    """Compile LLVM IR to assembly using llc"""
    asm_file = llvm_file.replace('.ll', '.s')
    
    try:
        # Use llc to compile LLVM IR to assembly with proper target
        # Use -filetype=asm to ensure we get assembly output
        result = subprocess.run(['llc', '-filetype=asm', '-o', asm_file, llvm_file], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Generated assembly: {asm_file}")
            return asm_file
        else:
            print(f"Error compiling LLVM IR: {result.stderr}")
            return None
    except FileNotFoundError:
        print("Error: llc (LLVM compiler) not found. Please install LLVM.")
        return None

def compile_llvm_directly_to_executable(llvm_file):
    """Compile LLVM IR directly to executable using clang"""
    exe_file = llvm_file.replace('.ll', '')
    
    try:
        # Try clang first (best for LLVM IR)
        result = subprocess.run(['clang', '-o', exe_file, llvm_file], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Generated executable: {exe_file}")
            return exe_file
        else:
            print(f"Clang failed, trying gcc: {result.stderr}")
            # Try gcc as fallback
            result = subprocess.run(['gcc', '-o', exe_file, llvm_file], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Generated executable: {exe_file}")
                return exe_file
            else:
                print(f"Error compiling LLVM IR with both clang and gcc: {result.stderr}")
                return None
    except FileNotFoundError:
        print("Error: Neither clang nor gcc found. Please install Clang or GCC.")
        return None

def compile_assembly_to_executable(asm_file):
    """Compile assembly to executable using gcc"""
    exe_file = asm_file.replace('.s', '')
    
    try:
        # Try gcc first, then clang if gcc fails
        result = subprocess.run(['gcc', '-o', exe_file, asm_file], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Generated executable: {exe_file}")
            return exe_file
        else:
            print(f"GCC failed, trying clang: {result.stderr}")
            # Try clang as fallback
            result = subprocess.run(['clang', '-o', exe_file, asm_file], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Generated executable: {exe_file}")
                return exe_file
            else:
                print(f"Error linking assembly with both gcc and clang: {result.stderr}")
                return None
    except FileNotFoundError:
        print("Error: Neither gcc nor clang found. Please install GCC or Clang.")
        return None

def main():
    parser = argparse.ArgumentParser(description="Scheil compiler - converts .scir to LLVM IR and assembly")
    parser.add_argument("file", help="Input .scir file")
    parser.add_argument("--llvm-only", action="store_true", help="Only generate LLVM IR")
    parser.add_argument("--asm-only", action="store_true", help="Generate LLVM IR and assembly, but don't link")
    parser.add_argument("--direct", action="store_true", help="Compile LLVM IR directly to executable (skip assembly)")
    args = parser.parse_args()
    
    if not args.file.endswith('.scir'):
        print("Error: Input file must have .scir extension")
        sys.exit(1)
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found")
        sys.exit(1)
    
    # Step 1: Convert .scir to LLVM IR
    llvm_file = compile_scir_to_llvm(args.file)
    if not llvm_file:
        sys.exit(1)
    
    if args.llvm_only:
        print("LLVM IR generation complete.")
        return
    
    if args.direct:
        # Direct compilation from LLVM IR to executable
        exe_file = compile_llvm_directly_to_executable(llvm_file)
        if not exe_file:
            sys.exit(1)
        print(f"Direct compilation complete! Executable: {exe_file}")
        print(f"Run with: ./{os.path.basename(exe_file)}")
        return
    
    # Step 2: Convert LLVM IR to assembly
    asm_file = compile_llvm_to_assembly(llvm_file)
    if not asm_file:
        sys.exit(1)
    
    if args.asm_only:
        print("Assembly generation complete.")
        return
    
    # Step 3: Link assembly to executable
    exe_file = compile_assembly_to_executable(asm_file)
    if not exe_file:
        sys.exit(1)
    
    print(f"Compilation complete! Executable: {exe_file}")
    print(f"Run with: ./{os.path.basename(exe_file)}")

if __name__ == "__main__":
    main()