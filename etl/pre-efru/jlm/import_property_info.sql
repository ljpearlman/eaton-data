set search_path = raw_jlm;

insert into report_file (file_name) values (:'fn');
insert into report (report_name)
   select regexp_replace(file_name, '/[^/]*$', '')
   from report_file on conflict do nothing;

update report_file f
   set report_id = r.report_id from report r
       where r.report_name = regexp_replace(f.file_name, '/[^/]*$', '');

create temporary table t_property_info (like property_info);
alter table t_property_info drop column report_id;
copy t_property_info from :'fn' with csv header;

insert into property_info(report_id, attr_name, attr_value)
   select f.report_id, t.attr_name, t.attr_value
   from report_file f join t_property_info t
   on f.file_name = :'fn';
   
;
