import argparse
import sys
from pathlib import Path

from src.pytsparser import PydanticToTSConvertor


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "infile", help="Input file path. Must be a python script with pydantic models"
    )
    parser.add_argument("outfile", help="Output file path. Should end in .ts")
    args = parser.parse_args()
    if args.infile is None:
        parser.print_help()
        return 1
    if args.outfile is None:
        parser.print_help()
        return 1
    infile = Path(args.infile)
    outfile = Path(args.outfile)
    if not infile.exists():
        print(f"Error: path {infile} does not exist")
        return 1
    if not outfile.parent.exists():
        print(
            f"Error: Cannot write to {outfile} because {outfile.parent} does not exist"
        )
        return 1
    with open(infile, "r") as fin, open(outfile, "w") as fout:
        parser = PydanticToTSConvertor(fin, fout)
        parser.parse()
    return 0


if __name__ == "__main__":
    sys.exit(main())
