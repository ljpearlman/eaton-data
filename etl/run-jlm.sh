usage="usage: $0 extract_directory"

extract_dir=$1
psql -f jlm.sql eaton
psql -f jlm_import_property -v vn=$extract_dir/0-property_info.csv eaton
psql -f jlm_import_scope -v vn=$extract_dir/1-scope.csv eaton
