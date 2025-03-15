from deriva.core import DerivaServer, ErmrestCatalog, get_credential, BaseCLI
from deriva.core.ermrest_model import builtin_types, Table, Column, Key, ForeignKey

def main(host, catalog_id):
    credentials = get_credential(host)
    server = DerivaServer('https', host, credentials)
    catalog = ErmrestCatalog.connect(server, catalog_id)
    model = catalog.getCatalogModel()
    schema = model.schemas["efru_data"]
#    Schema = model.create_schema({"schema_name": "efru_data"})

    schema.create_table(Table.define(
        "structure",
        [
            Column.define("accession_id", builtin_types.text, nullok=False),
            Column.define("remediation_state", builtin_types.text, nullok=False),
            Column.define("distance", builtin_types.text, nullok=False),
            Column.define("damage", builtin_types.text, nullok=False),
            Column.define("insurance", builtin_types.text, nullok=False),
            Column.define("relationship", builtin_types.text, nullok=False)
        ],
        key_defs = [
            Key.define(["accession_id"])
        ],
        fkey_defs = [
            ForeignKey.define(
                ["remediation_state"], "vocab", "remediation_state", ["name"]),
            ForeignKey.define(
                ["distance"], "vocab", "distance", ["name"]),
            ForeignKey.define(
                ["damage"], "vocab", "damage", ["name"]),
            ForeignKey.define(
                ["insurance"], "vocab", "insurance", ["name"]),
            ForeignKey.define(
                ["relationship"], "vocab", "relationship", ["name"])
            ]))

    schema.create_table(Table.define(
        "testing_company",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("url", builtin_types.text, nullok=True)
        ],
        key_defs = [
            Key.define(["name"])
        ]))

    schema.create_table(Table.define(
        "lab",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("url", builtin_types.text, nullok=True)
        ],
        key_defs = [
            Key.define(["name"])
        ]));    

    schema.create_table(Table.define(
        "report_file",
        [
            Column.define("file_name", builtin_types.text, nullok=False),
            Column.define("structure", builtin_types.text, nullok=False),
            Column.define("processed", builtin_types.boolean, nullok=False, default=False),
            Column.define("comments", builtin_types.text, nullok=True),
            Column.define("collection_date", builtin_types.date, nullok=True),
            Column.define("testing_company", builtin_types.text, nullok=False),
            Column.define("lab", builtin_types.text, nullok=False),
        ],
        key_defs = [
            Key.define(["file_name"])
        ],
        fkey_defs = [
            ForeignKey.define(
                ["structure"], "efru_data", "structure", ["RID"]),
            ForeignKey.define(
                ["testing_company"], "efru_data", "testing_company", ["name"]),
            ForeignKey.define(
                ["lab"], "efru_data", "lab", ["name"]),
            
            ]))

if __name__ == "__main__":
    cli=BaseCLI("Define structure table", None, 1, hostname_required=True, config_file_required=False)
    cli.parser.add_argument("--catalog-id", default="1")
    args=cli.parse_cli()
    main(args.host, args.catalog_id)
    

    
