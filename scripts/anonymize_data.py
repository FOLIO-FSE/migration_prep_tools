from faker import Faker
import csv
import os
import json
from pprint import pprint
import pandas
import argparse
import logging
from datetime import date, datetime
from helpers.percent_tracker import PercentTracker
from helpers.functions import check_folder, get_timestamp
from helpers.tool_logging import setup_logging

providers = [
    {"provider": "address"},
    {"provider": "barcode"},
    {"provider": "credit_card"},
    {"provider": "name"},
    {"provider": "first_name"},
    {"provider": "last_name"},
    {"provider": "date_of_birth", "params": {
        "minimum_age": 18, "maximum_age": 75}},
    {"provider": "date_this_century"},
    {"provider": "email", "params": {"domain": "fake.edu"}},
    {"provider": "phone_number"},
    {"provider": "prefix_nonbinary"},
    {"provider": "ssn"}
]


class AnonymizeData():
    def __init__(self):
        self.timestamp = get_timestamp()
        self.percent_tracker = PercentTracker(step=100)
        self.parser = argparse.ArgumentParser(
            description='Anonymize Delimited Data')

        self.parser.add_argument('--locale',
                                 help="Locale for provider", action="store")
        self.parser.add_argument('--generate-config',
                                 help="Generate anon_config.json", action=argparse.BooleanOptionalAction)
        self.parser.add_argument(
            'src_data', help="Path to delimited data", action="store")
        self.args = self.parser.parse_args()
        self.arg_dict = self.args.__dict__
        self.src_data = self.arg_dict["src_data"]
        self.locale = self.arg_dict["locale"]
        self.fake_factory = Faker([self.locale] if self.locale else "en-US")
        self.us_factory = Faker("en_US")
        self.delimiter = "\t" if os.path.splitext(
            self.arg_dict["src_data"])[1] == ".tsv" else ","
        self.source_rows = self.returnSourceData(self.src_data)

        self.fn = os.path.splitext(
            os.path.basename(self.arg_dict["src_data"]))[0]

        self.new_folder = check_folder(
            f"prep_output/anonymize_data/{self.fn}")
        self.config_path = os.path.join(self.new_folder, "anon_config.json")
        if os.path.exists(self.config_path):
            with open(self.config_path, mode="r", encoding='utf-8') as jsonfile:
                self.config_data = json.load(jsonfile)

    def generate_config(self):

        json_obj = {"config": {
            k: {} for k in self.source_rows[0].keys()}, "available_providers": providers, "documentation": "https://faker.readthedocs.io/en/stable/providers.html"}
        with open(self.config_path, mode='w', encoding="utf-8") as openfile:
            json.dump(json_obj, openfile)
        print()
        print(self.config_path)

    def setup_run(self):
        setup_logging(
            "", self.new_folder, self.timestamp
        )
        self.anon_keys = a.returnAnonData().keys()

    def returnSourceData(self, source_data):
        with open(source_data, mode='r', encoding="utf-8") as openfile:
            return [row for row in csv.DictReader(
                openfile, delimiter=self.delimiter)]

    def returnAnonData(self):
        anon_row = {}
        if not os.path.exists(self.config_path):
            e = FileExistsError(
                f"anon_config.json does not exist in {self.new_folder}.")
            logging.error(e)
            raise e

        for key, value in self.config_data["config"].items():
            if value:
                provider = value["provider"]
                valFunc = getattr(self.fake_factory, provider, None)
                if not valFunc and getattr(self.us_factory, provider, None):
                    valFunc = getattr(self.us_factory, provider, None)
                params = value["params"] if "params" in value else {}
                try:
                    row_value = valFunc(**params)
                except TypeError:
                    raise Exception(f"{provider} does not exist as a provider")
                if type(row_value) == date:
                    row_value = datetime.strftime(row_value, "%Y-%m-%d")
                anon_row[key] = row_value
        return anon_row

    def generateFakeUniq(self):
        uniq_vals = {k: {} for k in self.anon_keys}
        print()
        print("Generating fake data for each unique PII")
        self.percent_tracker.amount = len(self.source_rows)
        for row in self.source_rows:
            message = self.percent_tracker.print_message()
            if (message):
                logging.info(message)
            anon_row = self.returnAnonData()
            for key in self.anon_keys:
                if row[key]:
                    valKeys = uniq_vals[key].keys()
                    if row[key] not in valKeys:
                        uniq_vals[key][row[key]] = anon_row[key]
        return uniq_vals

    def fakeRow(self, row):
        row_keys = row.keys()
        has_pii = [key for key in row_keys if row[key]
                   and key in self.anon_keys]
        new_row = {**row}
        for key in has_pii:
            new_val = self.uniq_vals[key][row[key]]
            new_row[key] = new_val
        return new_row

    def run(self):
        self.uniq_vals = self.generateFakeUniq()
        ext = os.path.splitext(self.arg_dict["src_data"])[-1]
        dest_fp = os.path.join(
            self.new_folder, f"{self.fn}_anonymized_{self.timestamp}{ext}")
        new_rows = []
        new_rows = [self.fakeRow(row) for row in self.source_rows]
        with open(dest_fp, mode='w', encoding='utf-8') as openfile:
            csvwriter = csv.DictWriter(
                openfile, fieldnames=new_rows[0].keys(), delimiter=self.delimiter)
            csvwriter.writeheader()
            csvwriter.writerows(new_rows)
        print()
        print(dest_fp)


if __name__ == "__main__":
    a = AnonymizeData()
    if a.arg_dict["generate_config"]:
        a.generate_config()
    else:
        a.setup_run()
        a.run()
