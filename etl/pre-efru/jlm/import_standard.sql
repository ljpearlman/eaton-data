set search_path = raw_jlm;

insert into report_file (file_name) values (:'fn');
insert into report (report_name)
   select regexp_replace(file_name, '/[^/]*$', '')
   from report_file on conflict do nothing;

update report_file f
   set report_id = r.report_id from report r
       where r.report_name = regexp_replace(f.file_name, '/[^/]*$', '');

create temporary table t_standard (like standard);
alter table t_standard drop column report_id;
alter table t_standard drop column contaminant;
copy t_standard from :'fn' with csv;
select * from t_standard;

insert into standard(report_id, contaminant, surface, max_value)
   select r.report_id, :'cn', t.surface, t.max_value
   from report_file r join t_standard t
   on r.file_name = :'fn'
   where surface != 'Surface' and surface != ''
;   
