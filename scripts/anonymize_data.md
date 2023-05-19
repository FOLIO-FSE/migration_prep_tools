## Generate Config

`python scripts/anonymize_data.py --generate-config path/to/source/data`

## Edit Config

Match source data column with provider of fake data.
List of available providers: https://faker.readthedocs.io/en/stable/providers.html

```json
{
  "config": {
    "PATRN NAME": "name",
    "ADDRESS": "address",
    "ADDRESS2": "address",
    "TELEPHONE": "phone_number",
    "TELEPHONE2": "phone_number"
  }
}
```

## Run script

Optional: include `--locale` to create locale-appropriate fake data.

`python scripts/anonymize_data.py --locale es_MX "source_data/Patron Records December 2022.tsv"`
