# Pydantic model to TS convertor

A common use case is to write a FastAPI endpoint to service a JavaScript based front-end. Defining the FastAPI response model as a Pydantic model, one then wants to keep a set of Typescript definitions that stay in sync with these. This utility will convert (simple) Pydantic models into Typescript.

The package has no dependencies other than Pydantic.

## Example

Input:

```python
class Example(BaseModel):
    str_field: str
    int_field: int
    float_field: float
    list_of_ints: list[int]
    list_of_nullable: list[str | None]
    optional: Optional[bool]
```

Output:

```ts
export type Example = {
  str_field: string;
  int_field: number;
  float_field: number;
  list_of_ints: number[];
  list_of_nullable: Array<string | null>;
  optional: boolean | null;
};
```

## Setup

Install into your environment:

```bash
git clone url pydantic_to_ts
pip install ./pydantic_to_ts
```

## Command line arguments

```
usage: pydantic_to_ts [-h] infile outfile

positional arguments:
  infile      Input file path. Must be a python script with pydantic models
  outfile     Output file path. Should end in .ts

options:
  -h, --help  show this help message and exit
```

## Code coverage

`pytest --cov=src test/ --cov-report term-missing`
