from faker import Faker
import csv
import os
import json
import argparse
from datetime import datetime, date, timedelta
from random import choice


def random_birthdate():
    test_date1, test_date2 = date(1950, 1, 1), date(1995, 12, 31)
    res_dates = [test_date1]
    while test_date1 != test_date2:
        test_date1 += timedelta(days=1)
        res_dates.append(test_date1)
    res = choice(res_dates)
    return datetime.strftime(res, "%Y-%m-%d")


class PercentTracker():
    def __init__(self, step=1):
        self.amount = 0
        self.counter = 0
        self.start = datetime.now()
        self.step = step

    def restart_clock(self):
        self.start = datetime.now()

    def print_message(self, param=None):
        elapsed = datetime.now() - self.start
        self.counter += 1
        percentage = (float(self.counter) / float(self.amount)) * 100
        percent = round(percentage, 3)
        percent = format(percent, '.3f')
        if self.counter % self.step == 0:
            if param:
                print(elapsed, '\t', '{} of {}\t{}%'.format(
                    self.counter, self.amount, percent), '\t', param)
            else:
                print(elapsed, '\t', '{} of {}\t{}%'.format(
                    self.counter, self.amount, percent))


class AnonymizeData():
    def __init__(self):
        self.percent_tracker = PercentTracker(step=100)
        self.parser = argparse.ArgumentParser(
            description='Anonymize Delimited Data')
        self.parser.add_argument(
            'src_data', help="Path to delimited data", action="store")
        self.parser.add_argument(
            'data_dest', help="Destination for output files", action="store")
        self.parser.add_argument('--locale',
                                 help="Locale for provider", action="store")
        self.parser.add_argument('--generate-config',
                                 help="Generate anon_config.json", action=argparse.BooleanOptionalAction)
        self.args = self.parser.parse_args()
        self.arg_dict = self.args.__dict__
        self.locale = self.arg_dict["locale"]
        self.fake_factory = Faker([self.locale] if self.locale else "en-US")
        self.delimiter = "\t" if os.path.splitext(
            self.arg_dict["src_data"])[1] == ".tsv" else ","
        self.source_rows = self.returnSourceData(self.arg_dict["src_data"])
        self.anon_keys = self.returnAnonData().keys()

    def returnSourceData(self, source_data):
        with open(source_data, mode='r', encoding="utf-8") as openfile:
            return [row for row in csv.DictReader(
                openfile, delimiter=self.delimiter)]

    def returnAnonData(self):
        anon_row = {}
        config_path = "anon_config.json"
        us_factory = Faker("en_US")
        if not os.path.exists(config_path):
            raise FileExistsError(
                "anon_config.json does not exist in working folder.")
        with open(config_path, mode="r", encoding='utf-8') as jsonfile:
            config_data = json.load(jsonfile)
        for key, value in config_data.items():
            valFunc = getattr(self.fake_factory, value, None)
            if valFunc:
                anon_row[key] = valFunc()
            elif getattr(us_factory, value, None):
                vf = getattr(us_factory, value, None)
                anon_row[key] = vf()
            else:
                raise ValueError(
                    f"Faker does not include '{value}' as a provider\nhttps://faker.readthedocs.io/en/stable/locales.html")
        return anon_row

    def generateFakeUniq(self):
        uniq_vals = {k: {} for k in self.anon_keys}
        print()
        print("Generating fake data for each unique PII")
        self.percent_tracker.amount = len(self.source_rows)
        for row in self.source_rows:
            self.percent_tracker.print_message()
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

    def generate_config(self):
        columns = self.source_rows[0].keys()
        json_obj = {k: "" for k in self.source_rows[0].keys()}
        for row in self.source_rows:
            for column in columns:
                if not json_obj[column] and row[column]:
                    json_obj[column] = row[column]
        print(json_obj)

    def run(self):
        self.uniq_vals = self.generateFakeUniq()
        fp, ext = os.path.splitext(self.arg_dict["src_data"])
        data_dest = self.arg_dict["data_dest"]
        fn = os.path.basename(fp)
        timestamp = datetime.strftime(datetime.now(), "%Y%m%d-%H%M%S")
        dest_fp = os.path.join(
            data_dest, f"{fn}_anonymized_{timestamp}{ext}")
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
    print(a.arg_dict)
    print()
    if a.arg_dict["generate_config"]:
        a.generate_config()
    else:
        a.run()
