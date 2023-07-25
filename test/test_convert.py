import io

import pytest

from src.pydantic_to_ts.pytsparser import PydanticToTSConvertor

preamble = "from pydantic import BaseModel\n\n\n"


def test_ignores_non_pydantic_classes():
    fin = io.StringIO(
        """
class Foo:
    pass
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    fout.seek(0)
    assert fout.read() == ""


def test_can_write_type():
    fin = io.StringIO(
        preamble
        + """
class Example(BaseModel):
    str_field: str
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    fout.seek(0)
    result = fout.read().strip()
    assert result == "export type Example = {\n  str_field: string;\n};"


def test_can_write_multiple_types():
    fin = io.StringIO(
        preamble
        + """
class Example(BaseModel):
    str_field: str
    int_field: int
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    fout.seek(0)
    result = fout.read().strip()
    assert (
        result
        == """export type Example = {
  str_field: string;
  int_field: number;
};"""
    )


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("float", "number"),
        ("int", "number"),
        ("datetime", "string"),
        ("bool", "boolean"),
        ("dict", "any"),
        ("str", "string"),
        ("Optional[str]", "string | null"),
        ("list[str]", "string[]"),
        ("list[int]", "number[]"),
        ("list[float]", "number[]"),
        ("list[int | None]", "Array<number | null>"),
        ("list[float | None]", "Array<number | null>"),
    ],
)
def test_handles_basic_types(test_input, expected):
    fin = io.StringIO(
        preamble
        + f"""
class Example(BaseModel):
    field: {test_input}
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    fout.seek(0)
    result = fout.read().strip()
    assert result == f"export type Example = {{\n  field: {expected};\n}};"


def test_handles_previously_defined_models():
    fin = io.StringIO(
        preamble
        + """
class ModelA(BaseModel):
    str_field: str

class ModelB(BaseModel):
    field: ModelA
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    fout.seek(0)
    result = fout.read().strip()
    assert (
        result
        == """
export type ModelA = {
  str_field: string;
};

export type ModelB = {
  field: ModelA;
};
""".strip()
    )


def test_ignores_inner_config_class():
    fin = io.StringIO(
        preamble
        + """
class Example(BaseModel):
    str_field: str

    class Config:
        orm_mode = True
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    fout.seek(0)
    result = fout.read().strip()
    assert result == "export type Example = {\n  str_field: string;\n};"


def test_ignores_and_warns_on_other_inner_class(capfd):
    fin = io.StringIO(
        preamble
        + """
class Example(BaseModel):
    str_field: str

    class Something:
        orm_mode = True
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    out, err = capfd.readouterr()
    assert out == "Warning: Unknown inner class declaration Something on line 6\n"
    fout.seek(0)
    result = fout.read().strip()
    assert result == "export type Example = {\n  str_field: string;\n};"


def test_ignores_other_definitions_in_a_class(capfd):
    fin = io.StringIO(
        preamble
        + """
class Example(BaseModel):
    str_field: str

    def foo():
        pass
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    out, err = capfd.readouterr()
    assert out.startswith("Warning: Unhandled declaration <ast.FunctionDef")
    fout.seek(0)
    result = fout.read().strip()
    assert result == "export type Example = {\n  str_field: string;\n};"


def test_ignores_other_field_defs(capfd):
    fin = io.StringIO(
        preamble
        + """
from typing import Callable
class Example(BaseModel):
    str_field: str
    weird_field: Callable
"""
    )
    fout = io.StringIO()
    p = PydanticToTSConvertor(fin, fout)
    p.parse()
    out, err = capfd.readouterr()
    assert out == "Warning: Unhandled type Callable on line 8\n"
    fout.seek(0)
    result = fout.read().strip()
    assert (
        result == "export type Example = {\n  str_field: string;\n  weird_field: ;\n};"
    )
