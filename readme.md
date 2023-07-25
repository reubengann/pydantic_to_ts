# Pydantic model to TS convertor

## Setup

Install into your environment

## Command line arguments

```
usage: pyd_to_ts.py [-h] infile outfile

positional arguments:
  infile      Input file path. Must be a python script with pydantic models
  outfile     Output file path. Should end in .ts

options:
  -h, --help  show this help message and exit
```

## Code coverage

`pytest --cov=src test/ --cov-report term-missing`
