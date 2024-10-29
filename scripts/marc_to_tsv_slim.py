import csv
import logging
import argparse
import pandas as pd
import os
from pymarc import MARCReader
from helpers.functions import get_timestamp
from datetime import datetime

class MARCToTSV():
    def __init__(self):
        self.timestamp = get_timestamp()
        self.parser = argparse.ArgumentParser(
            description='MARC to TSV Slim CLI')
        self.parser.add_argument('--key-field',
                                 action="store", help="One row per MARC field (e.g. 001). Default one row per record.", default="*")
        self.parser.add_argument('--marc-fields',
                                 help="A list-like string of fields: '001,004,852'", action="store")
        self.parser.add_argument(
            'mrc_source', help="Path to MRC file", action="store")
        self.args = self.parser.parse_args()
        self.arg_dict = self.args.__dict__
        self.source_file_path = self.arg_dict["mrc_source"]
        self.key_field = self.arg_dict["key_field"]
        self.dest_file_path = f"{self.key_field}_results_{self.timestamp}.tsv"
        self.marc_fields = self.arg_dict["marc_fields"]

    def build_marc_dataframe(self):
        rows = []
        headers = []
        supp_fields = ["001"]
        if self.marc_fields:
            supp_fields += [s.strip() for s in self.marc_fields.split(",")]
        supp_fields = list(set(supp_fields))
        print()
        counter = 0
        print(f"{datetime.now()}\tStarting!")
        with open(self.source_file_path, mode='rb') as openmrc:
            reader = MARCReader(openmrc)
            for i, record in enumerate(reader):
                counter += 1
                if i > 0 and i % 10000 == 0:
                    print(f"{datetime.now()}\t{i}")
                item_fields = record.get_fields(self.key_field)
                if len(item_fields) and "001" in record:
                    other_fields = []
                    for f in supp_fields:
                        other_fields += record.get_fields(f)
                    for i in item_fields:
                        row = {}
                        all_fields = [i, *other_fields]
                        field_dict = {field.tag:[] for field in all_fields}
                        for field in all_fields:
                            field_dict[field.tag].append(field)
                        for tag in field_dict:
                            for field_idx, field in enumerate(field_dict[tag]):
                                subfields = field.subfields_as_dict()
                                if len(subfields):
                                    for subfield in list(subfields.keys()):
                                        for sub_idx, subfield_value in enumerate(subfields[subfield]):
                                            header = f"{tag}_{field_idx}_{subfield}_{sub_idx}"
                                            headers.append(header)
                                            row[header] = subfield_value
                                else:
                                    if field.is_control_field():
                                        header = f"{tag}"
                                    else:
                                        header += f"_{field_idx}"
                                    headers.append(header)
                                    row[header] = field.value()
                        rows.append(row)
        df = pd.DataFrame.from_records(rows, columns=sorted(list(set(headers))))
        df.to_csv(self.dest_file_path, sep="\t", index=False)
        print(f"{datetime.now()}\t{counter}")
        print()
        print(self.dest_file_path)

if __name__ == "__main__":
    m = MARCToTSV()
    m.build_marc_dataframe()



