import json
from helpers.functions import get_timestamp
import argparse
import os


class RmKey:
    def __init__(self):
        self.timestamp = get_timestamp()
        self.parser = argparse.ArgumentParser(description="Generate Fake Data")

        self.parser.add_argument("src_file", help="Path to source file", action="store")
        self.parser.add_argument("dest_file", help="Path to dest file", action="store")
        self.parser.add_argument("key", help="Key to remove from objects", action="store")
        self.args = self.parser.parse_args()
        self.arg_dict = self.args.__dict__
        self.source = self.arg_dict["src_file"]
        self.dest = self.arg_dict["dest_file"]
        self.key = self.arg_dict["key"]
        if not self.dest or self.dest == ".":
            basename = os.path.basename(self.source)
            self.dest = f"EDIT_{basename}"

    def run(self):
        with open(self.source, mode="r", encoding="utf-8") as openJson:
            lines = [json.loads(line) for line in openJson.readlines()]
        new_lines = []
        for line in lines:
            new_line = {k: v for k, v in line.items() if k != self.key}
            new_line = f"{json.dumps(new_line)}\n"
            new_lines.append(new_line)
        with open(self.dest, mode="w", encoding='utf-8') as openJson:
            openJson.writelines(new_lines)
        print()
        print(self.dest)


if __name__ == "__main__":
    r = RmKey()
    r.run()
