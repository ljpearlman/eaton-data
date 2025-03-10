python etl/ingest_file_list.py | sort | psql -c "copy efru_data.source_file(file_name,structure_id) from STDIN with csv" efru
