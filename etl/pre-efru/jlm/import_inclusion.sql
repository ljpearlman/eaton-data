set search_path = raw_jlm;

insert into report_file (file_name) values (:'fn');
insert into report (report_name)
   select regexp_replace(file_name, '/[^/]*$', '')
   from report_file on conflict do nothing;

update report_file f
   set report_id = r.report_id from report r
       where r.report_name = regexp_replace(f.file_name, '/[^/]*$', '');

create temporary table t_area_inclusion (like area_inclusion);
alter table t_area_inclusion drop column report_id;
copy t_area_inclusion from :'fn' with csv;

insert into area_inclusion(report_id, area_name, area_included)
   select r.report_id, t.area_name, t.area_included
   from report_file r join t_area_inclusion t
   on r.file_name = :'fn'
;   
