from deriva.core import DerivaServer, ErmrestCatalog, get_credential, BaseCLI
from deriva.core.ermrest_model import builtin_types, Table, Column, Key, ForeignKey
import json
import sys

def main(host, catalog_id, annotation_file):
    credentials = get_credential(host)
    server = DerivaServer('https', host, credentials)
    catalog = ErmrestCatalog.connect(server, catalog_id)
    model = catalog.getCatalogModel()
    model.annotations = json.load(open(annotation_file))
    model.apply()

if __name__ == "__main__":
    cli=BaseCLI("setup schema for raw data", None, 1, hostname_required=True, config_file_required=False)
    cli.parser.add_argument("--catalog-id", default="1")
    cli.parser.add_argument("--annotation-file", "-f", default="catalog_annotations.json")
    args=cli.parse_cli()
    main(args.host, args.catalog_id, args.annotation_file)
