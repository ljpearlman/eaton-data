set search_path = raw_jlm;

insert into report_file (file_name) values (:'fn');
insert into report (report_name)
   select regexp_replace(file_name, '/[^/]*$', '')
   from report_file on conflict do nothing;

update report_file f
   set report_id = r.report_id from report r
       where r.report_name = regexp_replace(f.file_name, '/[^/]*$', '');

create temporary table t_location (like location);
alter table t_location drop column report_id;
copy t_location from :'fn' with csv;

insert into location(report_id, location_name, location_comments)
   select r.report_id, t.location_name, t.location_comments
   from report_file r join t_location t
   on r.file_name = :'fn'
;   
