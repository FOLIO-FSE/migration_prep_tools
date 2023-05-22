## Running

```bash
usage: marc_to_tsv.py [-h] [--skip-null-rows | --no-skip-null-rows] [--key-field KEY_FIELD]
                      [--marc-fields MARC_FIELDS]
                      mrc_source

MARC to TSV Standalone CLI

positional arguments:
  mrc_source            Path to MRC file

optional arguments:
  -h, --help            show this help message and exit
  --skip-null-rows, --no-skip-null-rows
                        Skip rows without key field. Default false.
  --key-field KEY_FIELD
                        One row per MARC field (e.g. 001). Default one row per record.
  --marc-fields MARC_FIELDS
                        A list-like string of fields: '001,004,852'
```
