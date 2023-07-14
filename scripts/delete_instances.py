import uuid
import requests
import argparse
import logging
import os
from getpass import getpass
from folioclient import FolioClient
from helpers.functions import check_folder, get_timestamp, open_file
from helpers.tool_logging import setup_logging


class DeleteInstancesRecursive:
    def __init__(self):
        self.creds = open_file(os.path.abspath(
            "./folio_credentials.json"
            ), f_type="json"
        )
        self.timestamp = get_timestamp()
        self.parser = argparse.ArgumentParser(description="Delete Instances")
        self.parser.add_argument(
            "ids_file",
            help="Path to text file of new-line separate instance IDs",
            action="store",
        )
        self.parser.add_argument(
            "-p", dest="password", type=str, required=False
        )
        self.parser.add_argument(
            "--dry_run", dest="dry_run", action=argparse.BooleanOptionalAction
        )
        self.args = self.parser.parse_args()
        if not self.args.password:
            self.args.password = getpass()
        self.arg_dict = self.args.__dict__
        self.new_folder = check_folder(
            f"prep_output/delete_instances/{self.timestamp}"
        )
        setup_logging("", self.new_folder, self.timestamp)
        self.folio_client = FolioClient(
            **{
                **self.creds,
                "password": self.arg_dict["password"]
                }
        )
        self.dry_run = self.arg_dict["dry_run"]
        self.instances_to_delete = open_file(self.arg_dict["ids_file"])

    def do_work(self):
        stubrecord = ""
        instance_ids = self.instances_to_delete
        logging.info(f"Working on deleting {len(instance_ids)} instances")
        for instance_id in [id.strip() for id in instance_ids if id]:
            if not uuid.UUID(instance_id) and not uuid.UUID(instance_id).version >= 4:
                raise Exception(
                    f"id {instance_id} of Object to delete is not a proper UUID"
                )
            # instance_to_delete = self.folio_client.folio_get_single_object(f"/instance-storage/instances/{instance_id}")

            instance_to_delete = self.folio_client.folio_get_single_object(
                f"/inventory/items?query=instance.id=={instance_id}"
            )
            logging.info(f"Processing instance {instance_id}")
            self.delete_items(instance_to_delete)

            query = f'?query=(instanceId="{instance_id}")'
            holdings = list(
                self.folio_client.get_all(
                    "/holdings-storage/holdings", "holdingsRecords", query
                )
            )
            self.delete_holdings(holdings)

            srs = self.folio_client.folio_get_single_object(
                f"/source-storage/records/{instance_id}/formatted?idType=INSTANCE"
            )
            self.delete_srs(srs)
            logging.info(f"Deleting instance {instance_id}")
            self.delete_request("/instance-storage/instances", instance_id)
            stubrecord += (
                "=LDR  00000dam  2200000Ia 4500\n=999  ff$i" + instance_id + "\n\n"
            )

        logging.info(
            f"The stub record(s) below can be pasted into Marcedit to create records tofacilitate record deletion in EDS\n-------------------------------\n"
        )
        logging.info(stubrecord)

    def delete_items(self, instance_to_delete):
        item_iterator = 0
        totalRecords = 0

        totalRecords = instance_to_delete["totalRecords"]

        if totalRecords > 0:
            while item_iterator < totalRecords:
                logging.info("start item process")
                item = instance_to_delete["items"][item_iterator]["id"]
                holding = instance_to_delete["items"][item_iterator]["holdingsRecordId"]
                item_iterator += 1
                logging.info(
                    "Deleting item: " + item + " associated with holding ID " + holding
                )
                self.delete_request("/item-storage/items", item)
        else:
            logging.info("No items detected")

    def delete_holdings(self, holdings):
        holding_iterator = 0

        if holdings:
            for holding in holdings:
                holding = holding["id"]
                logging.info("Deleting holding: " + holding)
                self.delete_request(f"/holdings-storage/holdings", holding)
        else:
            logging.info("No holdings detected")

    def delete_srs(self, srs):
        id = srs["id"]

        if id is not None:
            logging.info("Deleting SRS: " + id)
            self.delete_request(f"/source-storage/records", id)
        else:
            logging.info("No SRS detected")

    def delete_request(self, path, object_id):
        parsed_path = path.rstrip("/").lstrip("/")
        url = f"{self.folio_client.okapi_url}/{parsed_path}/{object_id}"
        if not uuid.UUID(object_id) and not uuid.UUID(object_id).version >= 4:
            raise Exception(f"id {object_id} of Object to delete is not a proper UUID")
        if not self.dry_run:
            logging.info(f"DELETE {url}")
            req = requests.delete(url, headers=self.folio_client.okapi_headers)
            logging.info(req.status_code)
            logging.info(req.text)
            req.raise_for_status()
        else:
            logging.info(f"Dry run: DELETE {url}")

if __name__ == "__main__":
    d = DeleteInstancesRecursive()
    d.do_work()
