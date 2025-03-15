from deriva.core import DerivaServer, ErmrestCatalog, get_credential, BaseCLI
from deriva.core.ermrest_model import builtin_types, Table, Column, Key, ForeignKey

def main(host, catalog_id):
    credentials = get_credential(host)
    server = DerivaServer('https', host, credentials)
    catalog = ErmrestCatalog.connect(server, catalog_id)
    model = catalog.getCatalogModel()
    schema = model.schemas["vocab"]

    schema.create_table(Table.define(
        "substance_category",
        [
            Column.define("name", builtin_types.text, nullok=False),
            Column.define("description", builtin_types.text)
        ],
        key_defs = [
            Key.define(["name"])
        ]))

    table = model.table("vocab", "substance")
    table.create_column(Column.define("substance_category", builtin_types.text))
    table.create_fkey(
        ForeignKey.define(["substance_category"], "vocab", "substance_category", ["name"]))

if __name__ == "__main__":
    cli=BaseCLI("Define structure table", None, 1, hostname_required=True, config_file_required=False)
    cli.parser.add_argument("--catalog-id", default="1")
    args=cli.parse_cli()
    main(args.host, args.catalog_id)
    
