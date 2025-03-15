from deriva.core import DerivaServer, ErmrestCatalog, get_credential, BaseCLI
from deriva.core.ermrest_model import builtin_types, Table, Column, Key, ForeignKey

def main(host, catalog_id):
    credentials = get_credential(host)
    server = DerivaServer('https', host, credentials)
    catalog = ErmrestCatalog.connect(server, catalog_id)
    model = catalog.getCatalogModel()
    schema = model.schemas["vocab"]

    schema.create_table(Table.define(
        "analysis_method",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text),
            Column.define("url", builtin_types.text)
        ],
        key_defs = [
            Key.define(["name"])
        ]))

    schema.create_table(Table.define(
        "prep_method",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text),
            Column.define("url", builtin_types.text)
        ],
        key_defs = [
            Key.define(["name"])
        ]))

    schema.create_table(Table.define(
        "substance",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text),
            Column.define("url", builtin_types.text),
            Column.define("alternate_names", builtin_types['text[]'])
        ],
        key_defs = [
            Key.define(["name"])
        ]))    

    schema.create_table(Table.define(
        "unit",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text),
            Column.define("url", builtin_types.text),
            Column.define("alternate_names", builtin_types['text[]'])
        ],
        key_defs = [
            Key.define(["name"])
        ]))    

    schema = model.schemas["efru_data"]

    schema.create_table(Table.define(
        "sample",
        [
            Column.define("report_file", builtin_types.text, nullok=False),
            Column.define("sample_id", builtin_types.text, nullok=False),
            Column.define("lab_id", builtin_types.text),
            Column.define("collection_date", builtin_types.date),
            Column.define("location", builtin_types.text),
            Column.define("analysis_method", builtin_types.text),
            Column.define("prep_method", builtin_types.text)
        ],
        key_defs = [
            Key.define(["report_file", "sample_id"])
        ],
        fkey_defs = [
            ForeignKey.define(
                ["report_file"], "efru_data", "report_file", ["RID"]),
            ForeignKey.define(
                ["analysis_method"], "vocab", "analysis_method", ["name"]),
            ForeignKey.define(
                ["prep_method"], "vocab", "prep_method", ["name"])
            ]
        ))

    schema.create_table(Table.define(
        "result",
        [
            Column.define("sample", builtin_types.text, nullok=False),
            Column.define("substance", builtin_types.text, nullok=False),
            Column.define("measurement", builtin_types.text, nullok=False),
            Column.define("unit", builtin_types.text),
            Column.define("reporting_limit", builtin_types.text)
        ],
        key_defs = [
            Key.define(["sample", "substance"])
        ],
        fkey_defs = [
            ForeignKey.define(["sample"], "efru_data", "sample", ["RID"]),
            ForeignKey.define(["substance"], "vocab", "substance", ["name"]),
            ForeignKey.define(["unit"], "vocab", "unit", ["name"])
            ]))

if __name__ == "__main__":
    cli=BaseCLI("Define structure table", None, 1, hostname_required=True, config_file_required=False)
    cli.parser.add_argument("--catalog-id", default="1")
    args=cli.parse_cli()
    main(args.host, args.catalog_id)
