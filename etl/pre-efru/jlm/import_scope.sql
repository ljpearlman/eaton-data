set search_path = raw_jlm;

insert into report_file (file_name) values (:'fn');
insert into report (report_name)
   select regexp_replace(file_name, '/[^/]*$', '')
   from report_file on conflict do nothing;

update report_file f
   set report_id = r.report_id from report r
       where r.report_name = regexp_replace(f.file_name, '/[^/]*$', '');

create temporary table t_scope (like scope);
alter table t_scope drop column report_id;
copy t_scope from :'fn' with csv;

insert into scope(report_id, attr_name, attr_value)
   select r.report_id, t.attr_name, t.attr_value
   from report_file r join t_scope t
   on r.file_name = :'fn'
;   
