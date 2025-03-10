\copy raw_data.master_sheet from 'data/master_sheet.csv' with csv header

set search_path = efru_data;

insert into remediation_state("name")
   select distinct remediation_state from raw_data.master_sheet;

insert into distance("name")
   select distinct distance from raw_data.master_sheet;

insert into damage("name")
   select distinct damage from raw_data.master_sheet;

insert into insurance("name")
   select distinct coalesce(insurance, other_insurance) from raw_data.master_sheet;
   
insert into relationship("name")
   select distinct relationship from raw_data.master_sheet;

insert into structure (
   accession_id,
   remediation_state,
   distance,
   damage,
   insurance,
   relationship
 ) select
   accession_id,
   remediation_state,
   distance,
   damage,
   coalesce(insurance, other_insurance),
   relationship
   from raw_data.master_sheet
;   
