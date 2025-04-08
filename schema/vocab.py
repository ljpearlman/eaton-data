from deriva.core import DerivaServer, ErmrestCatalog, get_credential, BaseCLI
from deriva.core.ermrest_model import builtin_types, Table, Column, Key, ForeignKey

def main(host, catalog_id):
    credentials = get_credential(host)
    server = DerivaServer('https', host, credentials)
    catalog = ErmrestCatalog.connect(server, catalog_id)
    model = catalog.getCatalogModel()
    schema = model.create_schema({"schema_name": "vocab"})

    schema.create_table(Table.define(
        "remediation_state",
        [
            Column.define("name", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["name"])
        ]
    ))

    schema.create_table(Table.define(
        "distance",
        [
            Column.define("name", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["name"])
        ]
    ))

    schema.create_table(Table.define(
        "damage",
        [
            Column.define("name", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["name"])
        ]
    ))

    schema.create_table(Table.define(
        "insurance",
        [
            Column.define("name", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["name"])
        ]
    ))

    schema.create_table(Table.define(
        "relationship",
        [
            Column.define("name", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["name"])
        ]
    ))

    schema.create_table(Table.define(
        "report_type",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["name"])
        ]
    ))

    schema.create_table(Table.define(
        "file_format",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["name"])
        ]
    ))


    schema.create_table(Table.define(
        "data_method",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["name"])
        ]
    ))

    schema.create_table(Table.define(
        "location",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text)
        ],
        key_defs = [
            Key.define(["name"])
        ]
        ))

    schema.create_table(Table.define(
        "location_conversion",
        [
            Column.define("from_val", builtin_types.text, nullok=False),
            Column.define("to_val", builtin_types.text, nullok=False),
            Column.define("validated", builtin_types.boolean, nullok=False, default=False)
        ],
        key_defs = [
            Key.define(["from_val"])
        ],
        fkey_defs = [
            ForeignKey.define(["to_val"], "vocab", "location", ["RID"])
        ]));
    
if __name__ == "__main__":
    cli=BaseCLI("Define structure table", None, 1, hostname_required=True, config_file_required=False)
    cli.parser.add_argument("--catalog-id", default="1")
    args=cli.parse_cli()
    main(args.host, args.catalog_id)




