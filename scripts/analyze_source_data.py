import csv
import pandas
import matplotlib.pyplot as plt
from mdutils.mdutils import MdUtils
from helpers.tool_logging import setup_logging
import traceback
import xlsxwriter
import argparse
import logging
import time
import os


def check_folder(p):
    if not os.path.exists(p):
        os.makedirs(p)
    return p


class AnalyzeDelimitedSourceData():
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Analyze Delimited Source Data Standalone CLI')
        self.parser.add_argument(
            '--max', help="Estimated highest number of values in any controlled list (e.g. 50 locations, 5 itypes). Default 100.", action="store", default=100)
        self.parser.add_argument(
            'data_file_path', help="The csv or tsv file to be analyzed. If csv, all rows must have the same number. of columns", action="store")
        self.parser.add_argument('results_folder',
                                 action="store", help="Folder where you want the output to be saved.")
        self.args = self.parser.parse_args()
        self.arg_dict = self.args.__dict__
        self.data_file_path = self.arg_dict["data_file_path"]
        self.data_file_name = os.path.basename(self.data_file_path)
        self.results_folder = self.arg_dict["results_folder"]
        self.format = os.path.splitext(self.data_file_name)[-1]
        self.estimated_max_controlled = int(
            self.arg_dict["max"])
        setup_logging(
            "", check_folder(".logs"), time.strftime("%Y%m%d-%H%M%S")
        )
        logging.info("Let's get started!")

        # Create a new folder to save the resulting files in
        self.new_folder = check_folder(os.path.join(
            self.results_folder, time.strftime(
                f"{self.data_file_name}_%Y%m%d-%H%M%S")
        ))

        # Create a markdown file
        self.mdFile = MdUtils(
            file_name=os.path.join(
                self.new_folder, f"source_data_overview_{self.data_file_name}.md"
            ),
            title="Overview of source data fields and values",
        )

        # Create an xlsx file
        self.excel_writer = pandas.ExcelWriter(
            os.path.join(
                self.new_folder, f"source_data_fields_{self.data_file_name}.xlsx"
            ),
            engine="xlsxwriter",
        )

    def do_work(self):
        try:
            logging.info("Reading file into dataframe: %s",
                         self.data_file_path)
            data = self.read_file()

            # Write headers and and introduction to markdown file
            self.mdFile.new_header(level=1, title="Breakdown of source data")
            self.mdFile.new_paragraph(
                "Scroll down to learn about your legacy data.")

            logging.info("Analyzing the dataframe...")
            # Perform a hight level analysis of the data frame
            self.analyze_dataframe(data)

            # Write a new seciton in the markdown to analyze the individual fields
            self.mdFile.new_header(
                level=2, title="A closer look at the individual fields"
            )

            self.mdFile.new_paragraph(
                f"If the number of unique values in a field is less than 20, "
                f"the values will be represented in a pie chart. If the number"
                f"of unique values exceeds {self.estimated_max_controlled}, "
                f"recurring values will be counted as they may indicate"
                f"duplicate data. Up to {self.estimated_max_controlled + 100} "
                f"recurring values will be printed as a list."
            )

            self.mdFile.new_line(
                f"If the number of unique values exceeds {self.estimated_max_controlled},"
                f"the field will be assumed to contian free-text data. "
                f"Recurring values may be duplicates/indicate that there is "
                f"potential to express this in a controlled manner. A "
                f"maximum of {self.estimated_max_controlled + 100} recurring values "
                f"will therefor be printed to the spreadsheet."
            )

            # Loop through all the columns in the dataframe to analyze the data
            logging.info("Analyzing each column of the dataframe...")
            for idx, column in enumerate(data):
                self.mdFile.new_paragraph()
                self.analyze_column_data(idx, column, data[column])
                self.mdFile.new_line()

            # Create a table of content
            self.mdFile.new_table_of_contents(table_title="Contents", depth=3)

        except Exception as ee:
            logging.error(f"Failed to analyze the data: {ee}")
            traceback.print_exc()

        finally:
            self.save_files()
            logging.info(
                f"\nAll done! Your reports have been saved to {self.new_folder}"
            )

    def read_file(self):
        """Reads a csv, tsv or fwf file.

        Returns:
            _type_: A pandas dataframe.
        """

        accepted_formats = [".tsv", ".csv", ".fwf"]
        if self.format not in accepted_formats:
            raise ValueError("{} not an accepted format".format(self.format))

        with open(self.data_file_path) as file:
            if self.format == ".csv":
                data = pandas.read_csv(
                    file, sep=",", quoting=csv.QUOTE_NONE, dtype=object
                )
                data = data.replace(r"\n", " ", regex=True)

            elif self.format == ".tsv":
                data = pandas.read_csv(
                    file, sep="\t", quoting=csv.QUOTE_NONE, dtype=object
                )
                data = data.replace(r"\n", " ", regex=True)

            elif self.format == ".fwf":
                data = pandas.read_fwf(file)

        return data

    def analyze_dataframe(self, data):
        """_summary_

        Args:
            data (_type_): _description_
        """

        logging.info("The data contains the following fields:\n%s",
                     data.columns.values)
        self.mdFile.new_header(level=2, title="Data overview")
        self.mdFile.new_paragraph(
            f"Your file contains {len(data.index)} rows (records) and "
            f"{len(data.columns)} columns (fields)."
        )
        self.mdFile.new_paragraph("These are the present fields:")
        self.mdFile.new_line(str(data.columns.values))

        # Create a bar chart with an overview of all field contents
        bar_chart = self.create_bar_chart(data)

        self.mdFile.new_paragraph(
            self.mdFile.new_inline_image(text="Chart", path=bar_chart)
        )

        # Print the list of columns to spreadsheet
        self.write_values_to_excel("",
                                   "Field names",
                                   pandas.Series(data.columns.values),
                                   ["Source field"]
                                   )

    def analyze_column_data(self, idx, column_name, column_data):
        """_summary_

        Args:
            column_name (_type_): _description_
            column_data (_type_): _description_
        """
        try:
            # For this process, explicitly write out empty values as well
            column_data = column_data.fillna("no_value_in_data")
            value_counts = column_data.value_counts()
            recurring_values = value_counts[value_counts > 1]

            value_counts_table = value_counts.rename_axis("Source value").reset_index(
                name="Count"
            )
            recurring_values_table = recurring_values.rename_axis(
                "Source value"
            ).reset_index(name="Count")

            unique_values = column_data.unique()

            # Write to log unique values
            logging.info(
                f"Number of unique values in column {column_name}: {len(unique_values)}"
            )

            # Write to markdown report
            self.mdFile.new_header(level=3, title=column_name)
            self.mdFile.new_line(
                f"Total number of non-empty values: {column_data.count()}"
            )
            self.mdFile.new_line(
                f"Number of unique values: {len(unique_values)}")
            self.mdFile.new_line(
                f"Number of recurring values: {len(recurring_values)}")

            if 0 < len(unique_values) <= self.estimated_max_controlled:

                # Write the values to spreadsheet
                self.write_values_to_excel(
                    idx, column_name, value_counts_table)

                # Print a neat table containing all the values and counts
                self.mdFile.new_line(
                    value_counts_table.to_markdown(index=False))

                # If the number of unique values is less than estimated_max_controlled
                # Add a stylish pie chart to the markdown
                pie_chart = self.create_pie_chart(column_name, value_counts)

                self.mdFile.new_line(
                    self.mdFile.new_inline_image(text="Chart", path=pie_chart)
                )

            elif self.estimated_max_controlled < len(unique_values) < len(column_data):
                self.mdFile.new_paragraph(
                    f"This column contains more than {self.estimated_max_controlled} "
                    f"unique values. See spreadsheet for a list of up to "
                    f"{self.estimated_max_controlled + 100} recurring (duplicate) values."
                )
                # Write the values to spreadsheet
                self.write_values_to_excel(
                    idx,
                    column_name,
                    recurring_values_table[: self.estimated_max_controlled + 100]
                )

        except ValueError as ee:
            logging.error(ee)

    def create_bar_chart(self, data):
        """Create a bar chart showing how many times a field occurs in the data
        Args:
            data (_type_): _description_
        """

        plt.rcParams["font.size"] = 12.0
        data.count().plot.barh(figsize=(20, 10), color="royalblue")
        plt.title("Field overview")

        filepath = self.new_folder + "/" + "field_overview.svg"
        plt.savefig(filepath)
        plt.close()

        return "field_overview.svg"

    def create_pie_chart(self, column, value_counts):
        """_summary_

        Args:
            column (_type_): _description_
            value_counts (_type_): _description_

        Returns:
            _type_: _description_
        """

        # Escape dollar signs and replace empty values to avoid confusing matplotlib
        # TODO Figure out why replacing the dollar signs isn't working
        clean_value_counts = value_counts.replace({r"\$": ""}, regex=True)

        try:
            legend_strings = [
                f"{value}   {value_counts[value]}\n"
                for value in clean_value_counts.to_dict()
            ]

            # Insert this to show that there are more values than in the legend
            legend_strings.insert(20, "And more...")

            # Creating pie chart with legend
            plt.rcParams["figure.figsize"] = 20, 10
            fig, (ax1, ax2) = plt.subplots(
                ncols=2, gridspec_kw={"width_ratios": [2, 1]}
            )

            ax1.set_title(column)
            pie = ax1.pie(
                clean_value_counts,
                colors=plt.cm.tab20.colors,
            )

            # Only show legend for the 25 most common values
            ax2.legend(pie[0], legend_strings[:21], borderaxespad=0)
            ax2.axis("off")

            plt.tight_layout()

            # Save plot as svg image
            column_file_name = f"{column.replace('/', '_')}.svg"
            column_file_name = column_file_name.replace(" ", "_")
            column_file_name = column_file_name.replace("#", "_")
            filepath = f"{self.new_folder}/{column_file_name}"

            plt.savefig(filepath)
            plt.close()

        except Exception as ee:
            logging.error(f"Unable to create pie chart for {column}: {ee}")

        return column_file_name

    def write_values_to_excel(self, idx, name, content, header=True):
        """_summary_

        Args:
            name (_type_): _description_
            content (_type_): _description_
            header (bool, optional): _description_. Defaults to True.
        """
        try:
            content.to_excel(
                self.excel_writer,
                sheet_name=name[:30].replace("/", "-"),
                header=header,
                index=False,
            )
        except xlsxwriter.exceptions.DuplicateWorksheetName:
            content.to_excel(
                self.excel_writer,
                sheet_name=name[:30].replace("/", "-") + str(idx),
                header=header,
                index=False,
            )

    def save_files(self):
        """_summary_"""
        self.mdFile.create_md_file()
        self.excel_writer.close()


if __name__ == "__main__":
    a = AnalyzeDelimitedSourceData()
    a.do_work()
