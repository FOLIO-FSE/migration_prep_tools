import os
import markdown
import pdfkit
from lxml import etree
from datetime import datetime
from pprint import pprint
import re
import json
import sys

def get_abs_path(rel_path):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, rel_path)
    return filename

def convert_md(config_file):
    timestamp = datetime.strftime(datetime.now(), "%Y%m%d")
    with open(config_file, mode="r", encoding="utf-8") as openjson:
        config = json.load(openjson)
    email = config["email"]
    base_path = config["base_path"]
    tagsToDelete = config["tagsToDelete"]
    client_name = config["client_name"]
    iteration = config["iteration"]
    domain = config["domain"]
    reports_folder = f"{base_path}/iterations/{iteration}/reports"
    files_config = config["files"]
    styling = config["styling"]
    replacements = [
        "client_name", "email", "iteration"
    ]
    for key, value in styling.items():
        if type(value) == str:
            for r in replacements:
                value = value.replace(
                    f"[{r}]", config[r]
                )
        styling[key] = value
    new_folder = os.path.join(reports_folder, "pdf_versions", iteration)
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
        new_fp = new_fp.replace("report_", f"{domain}_")
        text = replace_tags(text, ["details", "summary", "b", "string"])
        html = markdown.markdown(text, extensions=["tables"])
        html_tree = etree.ElementTree(etree.fromstring(f"<html>{html}</html>"))
        for tag in tagsToDelete:
            tag_arr = html_tree.findall(f".//{tag}")
            for t in tag_arr:
                parent = t.getparent()
                parent.remove(t)
        html_string = etree.tostring(html_tree).decode("utf-8")
        print(os.path.relpath(new_fp))
        pdfkit.from_string(
            html_string,
            new_fp,
            options=styling,
            css=get_abs_path("helpers/report.css")
        )
    for f in md_files:
        generate_pdf(f)


if __name__ == "__main__":
    config_path = sys.argv[-1]
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Cannot find {config_path}")
    print()
    convert_md(config_path)
