"""
Scheil Parser
Copyright (c) 2025-2026 Webbrowser11
MIT License
"""
import os
import argparse
import sys
import re
# this will output an intermediate representation file (.scir).
# and then the compiler will take that and make LLVM IR from it.

import re

def replace_with_delimiters(output, variables):
    # 1️⃣ Replace placeholders like ${var}
    for k, v in variables.items():
        placeholder = f"${{{k}}}"
        output = output.replace(placeholder, v)

    # 2️⃣ Evaluate math inside str()
    matches = re.findall(r"str\(([^()]*)\)", output)
    for expr in matches:
        try:
            # Try to sum numbers if they look numeric
            parts = [p.strip() for p in expr.split("+")]
            all_nums = True
            total = 0.0

            for part in parts:
                if re.match(r"['\"].*['\"]", part) or any(c.isalpha() for c in part):
                    all_nums = False
                    break
                try:
                    total += float(eval(part))
                except Exception:
                    all_nums = False
                    break

            if all_nums:
                result = str(total)
            else:
                result = str(eval(expr))

            output = output.replace(f"str({expr})", result)
        except Exception as e:
            print(f"⚠️ Error evaluating {expr!r}: {e}")

    # 3️⃣ Only remove + signs that are outside math expressions and placeholders
    # Keep + signs inside variable contents or before/after digits
    output = re.sub(r'(?<!\d)\s*\+\s*(?!\d)', '', output)

    return output

def main(file):
    file = file[:-4]  # remove .scx
    file = rf"{file}.sctk"
    # read the token file first, then create new file and write to it.
    with open(file, "r") as f:
        filecontents = f.readlines()
        f.close()
    file = file[:-5]  # remove .sctk
    file = rf"{file}.scir"
    if not os.path.isfile(file):
        # create the file, then open it.
        with open(file, "w") as f:
            f.write("")  # create empty file.
    # this will be easier then opening and reading parts of the file at once.
    variables = {}
    with open(file, "a") as f:
        iterations = -1
        while True:
            iterations += 1
            currentline = filecontents[iterations].strip()
            if currentline == "EOF":
                break
            # okay interpreteing the file line by line.
            if currentline.startswith("VARIABLE(") and currentline.endswith(")"):
                varname = currentline[9:-1]
                varvalue = filecontents[iterations + 1].strip()
                if varvalue.startswith("VARIABLEVALUE(") and varvalue.endswith(")"):
                    varvalue = varvalue[14:-1]
                    variables[varname] = varvalue
                # add it to the varlist.
                variables.update({varname: varvalue})
            if currentline.startswith("OUTPUT(") and currentline.endswith(")"):
                output = currentline[7:-1]
                output = f"output {output}"
                # i don't know how to check for variables in the output string!!!!!!!!
                # wait yes i do wtf
                # broken will fix soon, like 6 or 7pm.
                output = replace_with_delimiters(output, variables)
                # kay now we gotta look for str() to turn something into a string.
                if "str(" in output and ")" in output:
                    start = output.index("str(") + 4
                    end = output.index(")", start)
                    toreplace = output[start:end]
                    output = output.replace(f"str({toreplace})", toreplace)
                # just add it to the file now, then we can write the compiler.
                f.write(f"{output}\n") # append to the file.
        f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheil lexer")
    parser.add_argument("file", help="File to lex")
    args = parser.parse_args()
    main(args.file)
    sys.exit()
