import os
import markdown
import pdfkit
from lxml import etree
from datetime import datetime
import re
import json
import sys


def convert_md(config_file):
    timestamp = datetime.strftime(datetime.now(), "%Y%m%d")
    with open("config.json", mode="r", encoding="utf-8") as openjson:
        config = json.load(openjson)
    email = config["email"]
    base_path = config["base_path"]
    tagsToDelete = config["tagsToDelete"]
    client_name = config["client_name"]
    iteration = config["iteration"]
    reports_folder = f"{base_path}/iterations/{iteration}/reports"
    files_config = config["files"]
    styling = config["styling"]
    for key, value in styling.items():
        new_value = value.replace("{client_name}", client_name)
        new_value = value.replace("{email}", email)
        styling[key] = new_value
    new_folder = os.path.join(base_path, "pdf_versions", iteration)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
    if files_config["all_md_files"]:
        md_files = [
            f.path for f in os.scandir(reports_folder) if f.name.endswith("md")
        ]

    def replace_tags(text, tags):
        for tag in tags:
            text = text.replace(f"<{tag}>", "")
            text = text.replace(f"</{tag}>", "")
        return text

    def generate_pdf(fp):
        with open(fp, mode="r", encoding="utf-8") as input_file:
            text = input_file.read()
            gen_stats = "## General statistics"
            text = text.replace(gen_stats, f"\n{gen_stats}")
        f = re.findall(r"##\s[^\w]", text)
        if f:
            text = text.replace(f[0], "\n## Success rate\n")
        fn = os.path.basename(fp).replace(".md", ".pdf")
        new_fp = os.path.join(new_folder, f"{timestamp}_{fn}")
        new_fp = new_fp.replace("_transform", "_01_transform")
        new_fp = new_fp.replace("_post", "_02_post")
        text = replace_tags(text, ["details", "summary", "b", "string"])
        html = markdown.markdown(text, extensions=["tables"])
        html_tree = etree.ElementTree(etree.fromstring(f"<html>{html}</html>"))
        for tag in tagsToDelete:
            tag_arr = html_tree.findall(f".//{tag}")
            for t in tag_arr:
                parent = t.getparent()
                parent.remove(t)
        html_string = etree.tostring(html_tree).decode("utf-8")
        print(os.path.basename(new_fp))
        pdfkit.from_string(
            html_string,
            new_fp,
            options=styling,
            css="helpers/report.css",
        )
    for f in md_files:
        generate_pdf(f)


if __name__ == "__main__":
    config_path = sys.argv[-1]
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Cannot find {config_path}")
    convert_md(config_path)
