# migration_prep_tools

This repo is a slimmed down and curated version of https://github.com/FOLIO-FSE/service_tools. It includes some of the most common service tools as standalone scripts.

## Requirements

- Python >= 3.9
- pip >= 23

## Setup

**Create virtual environment if it doesn't already exist**

`python -m venv venv`

**Activate virtual environment**

- MacOS: `source activate venv/bin/scripts`
- Windows: `call venv\Scripts\activate.bat`

**Install requirements**

`python -m pip install -r requirements.txt`

## Running

The scripts can be copied to a different folder as long as:

1. `requirements.txt` are installed at that location (recommended in a `venv`)
2. Both the `*.py` file and `helpers` folder are copied.

## Developing

**Each standalone script should have its own help text defined by argparse.**

`python scripts/theScript.py --help`

**Add any new packages to requirements.txt**

`python -m pip freeze > requirements.txt`

**Add AT LEAST the arg parse help text to scripts/READMEs**

https://github.com/FOLIO-FSE/migration_prep_tools/blob/add-scripts/scripts/READMEs/analyze_source_data.md
