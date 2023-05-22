## Generate Config

`python scripts/anonymize_data.py --generate-config path/to/source/data`

## Edit Config

Match source data column with provider of fake data.
List of available providers: https://faker.readthedocs.io/en/stable/providers.html

```json
{
  "config": {
    "Card": {},
    "Title": { "provider": "prefix_nonbinary" },
    "Name": { "provider": "last_name" },
    "First name": { "provider": "first_name" },
    "Email": { "provider": "email", "params": { "domain": "fake-whu.edu" } },
    "Date of birth": {
      "provider": "date_of_birth",
      "params": { "minimum_age": 18, "maximum_age": 25 }
    },
    "Category": {},
    "Library": {},
    "Note": {}
  }
}
```

## Running

```bash
usage: anonymize_data.py [-h] [--locale LOCALE] [--generate-config | --no-generate-config] src_data

Anonymize Delimited Data

positional arguments:
  src_data              Path to delimited data

optional arguments:
  -h, --help            show this help message and exit
  --locale LOCALE       Locale for provider
  --generate-config, --no-generate-config
                        Generate anon_config.json
```
