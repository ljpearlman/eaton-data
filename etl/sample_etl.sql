set search_path = efru_data;

create temporary table t_sample (
    report_file text,
    sample_id text,
    lab_id text,
    collection_date text,
    location text,
    lab_methods text,
    collection_method text
);

\copy t_sample from '/tmp/sample.csv' with csv header

insert into vocab.lab_method(name)
   select distinct regexp_split_to_table(lab_methods, '\|')
   from t_sample
   where lab_methods is not null
   on conflict do nothing
;   

insert into vocab.collection_method(name)
   select distinct collection_method
   from t_sample
   where collection_method is not null
   on conflict do nothing
;   

insert into sample (
   report_file,
   sample_id,
   lab_id,
   collection_date,
   location,
   collection_method
)
select
   f."RID",
   s.sample_id,
   s.lab_id,
   s.collection_date::date,
   s.location,
   s.collection_method
from t_sample s
join report_file f on s.report_file = f.file_name
on conflict do nothing;

insert into sample_lab_method (
   sample,
   lab_method
) select
   s."RID",
   regexp_split_to_table(t.lab_methods, '\|')   
from sample s
join report_file f on f."RID" = s.report_file
join t_sample t on t.report_file = f.file_name
where t.sample_id = s.sample_id;

create temporary table t_result (
   report_file text not null,
   sample_id text not null,
   substance text,
   measurement text,
   unit text,
   reporting_limit text
);

\copy t_result from '/tmp/result.csv' with csv header

insert into vocab.substance(name)
  select distinct substance from t_result where substance is not null
  on conflict do nothing
;

insert into vocab.unit(name)
  select distinct unit from t_result where unit is not null
  on conflict do nothing
;


insert into result(
   sample,
   substance,
   measurement,
   unit,
   reporting_limit
)
   select s."RID",
   r.substance,
   r.measurement,
   r.unit,
   r.reporting_limit
from t_result r
join report_file f on f.file_name = r.report_file
join sample s on s.report_file = f."RID" and s.sample_id = r.sample_id
on conflict do nothing;
