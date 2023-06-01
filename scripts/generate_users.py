from faker import Faker
from random import randint, choice
from datetime import datetime
import csv
import math
import os
import argparse
from helpers.functions import check_folder, get_timestamp

default_groups = [
    {'folio_code': 'Library staff', 'percentage': '0.1'},
    {'folio_code': 'Students', 'percentage': '0.7'},
    {'folio_code': 'Alumni', 'percentage': '0.2'}
]


class GenerateUsers():
    def __init__(self):
        self.timestamp = get_timestamp()
        self.parser = argparse.ArgumentParser(
            description='Generate Fake Data')

        self.parser.add_argument('-l', '--locale',
                                 help="Locale for provider. Default: 'en_US'",
                                 action="store", default="en_US")
        self.parser.add_argument('-n', '--num',
                                 help="Number of fake users. Default: 100",
                                 action="store", default="100")
        self.parser.add_argument('-d', '--domain',
                                 help="Fake domain for email addresses. Default: fake-ebsco.com",
                                 action="store", default="fake-ebsco.com")
        self.parser.add_argument('-u', '--user-groups',
                                 help="Text file of user groups.",
                                 action="store")
        self.args = self.parser.parse_args()
        self.arg_dict = self.args.__dict__
        self.locale = self.arg_dict["locale"]
        self.num = int(self.arg_dict["num"])
        self.user_groups = self.arg_dict["user_groups"]
        self.new_folder = check_folder(
            "prep_output/generate_users")
        self.report_name = os.path.join(
            self.new_folder, f"{self.timestamp}-{self.locale}.tsv")
        self.fake_factory = Faker([self.locale] if self.locale else "en-US")

    def generate_person(self, patron_group, note=""):
        domain = self.arg_dict["domain"]
        first_name = self.fake_factory.first_name()
        last_name = self.fake_factory.last_name()
        barcode = self.fake_factory.ean(prefixes=('00'), length=8)
        email = f"{first_name[0].lower()}{last_name}{randint(10, 99)}@{domain}".replace(
            " ", "").replace("'", "").lower()
        return {
            'barcode': barcode,
            'externalSystemId': barcode,
            'legacyIdentifier': email,
            'note': note,
            'patronGroup': patron_group,
            'personal.dateOfBirth': datetime.strftime(self.fake_factory.date_of_birth(
                **{"minimum_age": 18, "maximum_age": 75}
            ), "%Y-%m-%d"),
            'personal.email': email,
            'personal.firstName': first_name,
            'personal.lastName': last_name,
            'personal.addresses[0].countryId': self.fake_factory.current_country_code(),
            'personal.addresses[0].addressLine1': self.fake_factory.street_address(),
            'personal.addresses[0].city': self.fake_factory.city(),
            'personal.addresses[0].postalCode': self.fake_factory.postcode(),
            'username': email.split("@")[0]
        }

    def calculate_groups(self):
        groups = default_groups
        if self.user_groups:
            with open(self.user_groups, mode='r', encoding='utf-8') as openfile:
                reader = csv.DictReader(openfile, delimiter="\t")
                groups = [row for row in reader]
        group_counts = {}
        for group in groups:
            code = group["folio_code"]
            amt = math.floor(float(group["percentage"])*self.num)
            group_counts[code] = amt
        return group_counts

    def run(self):
        group_counts = self.calculate_groups()
        note_count = math.floor(self.num*0.3)

        def get_group():
            group = ""
            groups = [k for k, v in group_counts.items()]
            for k, v in group_counts.items():
                if v > 0:
                    group = k
                    v -= 1
                    group_counts[k] = v
                    break
            return group if group else choice(groups)
        people = []
        for i in range(self.num):
            patron_group = get_group()
            note = ""
            if randint(1, self.num) < note_count:
                note = self.fake_factory.paragraph(nb_sentences=randint(1, 3))
            person = self.generate_person(patron_group, note)
            people.append(person)
        with open(self.report_name, mode="w", encoding="utf-8") as csvfile:
            headers = people[0].keys()
            writer = csv.DictWriter(
                csvfile, fieldnames=headers, delimiter="\t")
            writer.writeheader()
            writer.writerows(people)


if __name__ == "__main__":
    g = GenerateUsers()
    g.run()
