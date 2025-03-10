create schema eaton_raw;

create table eaton_raw.eaton_sheet (
  upload_time timestamp,
  address text,
  test_date date,
  testing_company text,
  testing_lab text,
  test_types text,
  contaminants_found text,
  concentrations text,
  recommended_remediation text,
  hvac_running_before_cleaning text,
  report_url text,
  dummy text
 );


