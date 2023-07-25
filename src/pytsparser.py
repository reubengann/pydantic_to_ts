import ast
from io import TextIOWrapper
from typing import Any

TYPEMAP = {
    "str": "string",
    "int": "number",
    "datetime": "string",
    "bool": "boolean",
    "float": "number",
    "dict": "any",
}


class PyTSParser:
    def __init__(self, fin: TextIOWrapper, fout: TextIOWrapper) -> None:
        self.fin = fin
        self.fout = fout
        self.recognized_types = set()
        self.current_line = 0

    def parse(self):
        tree = ast.parse(self.fin.read())
        for node in ast.walk(tree):
            if is_pydantic_model(node):
                d = node.__dict__
                self.fout.write(f"export type {d['name']} = {{\n")
                self.recognized_types.add(d["name"])
                body = d["body"]
                for b in body:
                    if isinstance(b, ast.AnnAssign):
                        self.current_line = b.lineno
                        self.fout.write("  ")
                        name = b.target.__dict__["id"]
                        self.fout.write(f"{name}: ")
                        self.write_type(b.__dict__["annotation"])
                        self.fout.write(";\n")
                    elif isinstance(b, ast.ClassDef):
                        if b.name == "Config":
                            pass  # This is just a config member
                        else:
                            print(
                                f"Warning: Unknown inner class declaration {b.name} on line {self.current_line}"
                            )
                    else:
                        print(
                            f"Warning: Unhandled declaration {b} on line {self.current_line}"
                        )
                self.fout.write("};\n\n")

    def write_type(self, annot: Any):
        if isinstance(annot, ast.Name):
            self.handle_name(annot)
        elif isinstance(annot, ast.BinOp):
            self.write_type(annot.left)
            self.fout.write(" | ")
            self.write_type(annot.right)
        elif isinstance(annot, ast.Constant):
            self.handle_constant(annot)
        elif isinstance(annot, ast.Subscript):
            self.handle_subscript(annot)
        else:
            print(f"Warning: Unhandled type {type(annot)} on line {self.current_line}")

    def handle_constant(self, annot: ast.Constant):
        if annot.value is None:
            self.fout.write("null")
        else:
            print(
                f"Warning: Unhandled constant value {annot.value} on line {self.current_line}"
            )

    def handle_name(self, annot: ast.Name):
        if annot.id in TYPEMAP:
            self.fout.write(TYPEMAP[annot.id])
        elif annot.id in self.recognized_types:
            self.fout.write(annot.id)
        else:
            print(f"Warning: Unhandled type {annot.id} on line {self.current_line}")

    def handle_subscript(self, annot: ast.Subscript):
        if not isinstance(annot.value, ast.Name):
            print(
                f"Warning: Unhandled generic type argument {annot.value} on line {self.current_line}"
            )
            return
        if annot.value.id == "list":
            if isinstance(annot.slice, ast.Name):
                self.write_type(annot.slice)
                self.fout.write("[]")
            else:
                self.fout.write("Array<")
                self.write_type(annot.slice)
                self.fout.write(">")
        elif annot.value.id == "Optional":
            self.write_type(annot.slice)
            self.fout.write(" | null")
        else:
            print(
                f"Warning: Unhandled generic type {annot.value.id} on line {self.current_line}"
            )


def is_pydantic_model(node: ast.AST) -> bool:
    if not isinstance(node, ast.ClassDef):
        return False
    if len(node.bases) == 0:
        return False
    base = node.bases[0]
    if base.__dict__["id"] != "BaseModel":
        return False
    return True
