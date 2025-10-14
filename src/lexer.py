"""
Scheil Lexer
Copyright (c) 2025-2026 Webbrowser11
MIT License
"""

import os
import sys
import argparse


TOKEN_TYPES = [
    "INT",
    "FLOAT",
    "PLUS",
    "MINUS",
    "MULTIPLY",
    "DIVIDE",
    "STRING",
    "VARIABLE",
    "COMMENT",
    "VARIABLEVALUE",
    "OUTPUT",
    "EOF"
]


def parse_varvalue(varvalue: str):
    """Convert variable value into correct type if possible."""
    varvalue = varvalue.strip()
    if not varvalue:
        return None

    # String literal
    if varvalue.startswith('"') and varvalue.endswith('"'):
        return varvalue[1:-1]

    # Try float
    if "." in varvalue:
        try:
            return float(varvalue)
        except ValueError:
            return varvalue  # leave raw

    # Try int
    try:
        return int(varvalue)
    except ValueError:
        return varvalue  # leave raw


def tokenize(filecontents, tokenfile):
    for line in filecontents:
        currentline = line.strip()

        if currentline.startswith("//"):  # comment
            continue # skip comments FULLY

        elif currentline.startswith("let "):  # variable declaration
            assignment = currentline[4:].strip()
            if "=" not in assignment:
                continue

            varname, rawvalue = assignment.split("=", 1)
            varname = varname.strip()
            varvalue = parse_varvalue(rawvalue)

            with open(tokenfile, "a") as tf:
                tf.write(f"VARIABLE({varname})\n")
                tf.write(f"VARIABLEVALUE({varvalue})\n")

        elif currentline.startswith("output(") and currentline.endswith(")"):
            outputvalue = currentline[7:-1].strip()
            with open(tokenfile, "a") as tf:
                tf.write(f"OUTPUT({outputvalue})\n")

        elif currentline == "":
            with open(tokenfile, "a") as tf:
                tf.write("\n")

    # End of file
    with open(tokenfile, "a") as tf:
        tf.write("EOF\n")


def main(filepath):
    tokenfile = os.path.splitext(filepath)[0] + ".sctk"

    with open(filepath, "r") as f:
        filecontents = f.readlines()

    if os.path.isfile(tokenfile):
        os.remove(tokenfile)

    open(tokenfile, 'x').close()

    tokenize(filecontents, tokenfile)

    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheil lexer")
    parser.add_argument("file", help="File to lex")
    args = parser.parse_args()
    main(args.file)