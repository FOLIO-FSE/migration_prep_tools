import csv
import logging
import argparse
import pandas
import os
import time
from pymarc import MARCReader
from helpers.tool_logging import setup_logging


class MARCToTSV():
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='MARC to TSV Standalone CLI')
        self.parser.add_argument(
            '--skip-null-rows', help="Skip rows without key field. Default false.", action=argparse.BooleanOptionalAction)
        self.parser.add_argument('--key-field',
                                 action="store", help="One row per MARC field (e.g. 001). Default one row per record.", default="*")
        self.parser.add_argument('--marc-fields',
                                 help="A list-like string of fields: '001,004,852'", action="store")
        self.parser.add_argument(
            'mrc_source', help="Path to MRC file", action="store")
        self.parser.add_argument(
            'tsv_dest', help="TSV Destination", action="store")
        self.args = self.parser.parse_args()
        self.arg_dict = self.args.__dict__
        self.source_file_path = self.arg_dict["mrc_source"]
        self.save_to_file = self.arg_dict["tsv_dest"]
        self.key_field = self.arg_dict["key_field"]
        self.marc_fields = self.arg_dict["marc_fields"]
        self.skip_null_rows = self.arg_dict["skip_null_rows"]
        setup_logging(
            "", os.path.dirname(
                self.save_to_file), time.strftime("%Y%m%d-%H%M%S")
        )
        self.dest = ""

    def do_work(self):
        with open(self.source_file_path, "rb") as marc_file:
            reader = MARCReader(marc_file, "rb", permissive=True)
            list_of_records = []
            invalid_records = 0
            records_wuithout_main_field = 0

            for r_i, record in enumerate(reader):
                record_number = r_i + 1
                record_dict = {}

                main_field_tag = self.key_field
                marc_fields = []
                if self.marc_fields:
                    marc_fields = self.marc_fields.split(",")

                try:
                    main_field_occurences = record.get_fields(main_field_tag)
                    if self.skip_null_rows == False and not main_field_occurences:
                        main_field_tag = "*"

                    if main_field_tag == "*":
                        for marc_field in marc_fields:
                            for i, field in enumerate(record.get_fields(marc_field)):
                                self.get_values(field, record_dict, i)
                        list_of_records.append(record_dict)

                    else:
                        if self.skip_null_rows == True and not main_field_occurences:
                            records_wuithout_main_field += 1
                        else:
                            for i, main_field in enumerate(main_field_occurences):
                                record_dict = {}
                                self.get_values(main_field, record_dict)

                                for marc_field in marc_fields:
                                    for i, field in enumerate(
                                        record.get_fields(marc_field)
                                    ):
                                        self.get_values(field, record_dict, i)

                                list_of_records.append(record_dict)

                except AttributeError as ae:
                    logging.error(f"{record_number}\t{ae}\t{record}")
                    invalid_records += 1

                if record_number % 5000 == 0:
                    logging.info(f"{record_number} records processed.")

            field_df = pandas.DataFrame(list_of_records)

            logging.info("\n\n")
            logging.info(f"Records processed: {record_number}")
            logging.info(
                f"Invalid records (failed to read): {invalid_records}")
            logging.info(
                f"Records with no {main_field_tag}: {records_wuithout_main_field}")
            logging.info(f"Rows created: {len(field_df)}")
            logging.info("\n\n")
            logging.info(field_df.head())

            field_df.to_csv(
                self.save_to_file,
                index=False,
                sep="\t",
                quoting=csv.QUOTE_MINIMAL,
                escapechar="\\",
                doublequote=False,
            )

    def get_values(self, field, record_dict, i="0"):
        if hasattr(field, "subfields"):
            for code in list(field.subfields_as_dict().keys()):
                for subfield in field.get_subfields(code):
                    clean_subfield = subfield.replace('\t', ' ')
                    header = field.tag + "_" + str(i) + "_" + code
                    if header in record_dict:
                        # print(f"Repeated subfield {code} in {field_to_csv}")
                        record_dict[header] = f"{record_dict[header]} ; {clean_subfield}"
                    else:
                        record_dict[header] = clean_subfield
        else:
            header = field.tag
            clean_value = field.value().replace('\t', ' ')
            record_dict[header] = clean_value


if __name__ == "__main__":
    m = MARCToTSV()
    m.do_work()
