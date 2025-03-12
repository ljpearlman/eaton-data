python etl/ingest_file_list.py | sort | psql -c "copy efru_data.report_file(file_name,structure) from STDIN with csv" efru
