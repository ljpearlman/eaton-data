create temporary table t (
   file_name text primary key,
   structure_id text not null,
   processed boolean not null,
   comments text
);

\copy t from 'report_file.csv' with csv

insert into efru_data.report_file(
   file_name,
   structure,
   processed,
   comments
   )
select
   t.file_name,
   s."RID",
   t.processed,
   t.comments
from t
join efru_data.structure s on t.structure_id = s.accession_id
on conflict do nothing;

