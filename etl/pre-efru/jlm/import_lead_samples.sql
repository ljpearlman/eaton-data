set search_path = raw_jlm;

insert into report_file (file_name) values (:'fn');
insert into report (report_name)
   select regexp_replace(file_name, '/[^/]*$', '')
   from report_file on conflict do nothing;

update report_file f
   set report_id = r.report_id from report r
       where r.report_name = regexp_replace(f.file_name, '/[^/]*$', '');

create temporary table t_sample (like sample);
alter table t_sample drop column report_id;
alter table t_sample drop column contaminant;
alter table t_sample drop column material;
alter table t_sample drop column result;
alter table t_sample drop column friable;
alter table t_sample drop column condition;

copy t_sample from :'fn' with csv;

insert into sample(report_id, report_sample_id, contaminant, location, regulated_level, concentration)
   select r.report_id, t.report_sample_id, :'cn', t.location, t.regulated_level, t.concentration
   from report_file r join t_sample t
   on r.file_name = :'fn'
;   
