## Running

```bash
usage: analyze_source_data.py [-h] [--max MAX] data_file_path

Analyze Delimited Source Data Standalone CLI

positional arguments:
  data_file_path  The csv or tsv file to be analyzed. If csv, all rows must have the same number. of columns

optional arguments:
  -h, --help      show this help message and exit
  --max MAX       Estimated highest number of values in any controlled list (e.g. 50 locations, 5 itypes).
                  Default 100.
```
