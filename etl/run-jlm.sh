usage="usage: $0 extract_directory contaminant"

extract_dir=$1; shift
contaminant=$1; shift

if [ -f $extract_dir/property_info.csv ]; then
    psql -f jlm/import_property_info.sql -v fn=$extract_dir/property_info.csv eaton
fi

if [ -f $extract_dir/scope.csv ]; then
    psql -f jlm/import_scope.sql -v fn=$extract_dir/scope.csv eaton
fi

if [ -f $extract_dir/locations.csv ]; then
    python jlm/fix_locations.py $extract_dir/locations.csv > $extract_dir/locations_fixed.csv
    psql -f jlm/import_location.sql -v fn=$extract_dir/locations_fixed.csv eaton
fi

if [ -f $extract_dir/inclusions.csv ]; then
    python jlm/fix_inclusion.py $extract_dir/inclusions.csv > $extract_dir/inclusions_fixed.csv
    psql -f jlm/import_inclusion.sql -v fn=$extract_dir/inclusions_fixed.csv eaton
fi

for f in $extract_dir/samples_[0-9].csv; do
    if [ -e $f ]; then
	new=`echo $f | sed -e 's/.csv/_fixed.csv/'`
	python jlm/fix_samples.py $f > $new
	psql -f jlm/import_samples.sql -v fn=$new -v cn=$contaminant eaton
    fi
done

if [ -f $extract_dir/samples_lead.csv ]; then
    psql -f jlm/import_lead_samples.sql -v fn=$extract_dir/samples_lead.csv -v cn=$contaminant eaton
fi
