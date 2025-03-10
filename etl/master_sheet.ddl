create schema raw_data;

create table raw_data.master_sheet (
   accession_id text primary key,
   remediation_state text not null,
   distance text not null,
   damage text not null,
   insurance text,
   other_insurance text,
   relationship text not null
);

create schema efru_data;
set search_path = efru_data;

create table remediation_state ("name" text primary key);
create table distance ("name" text primary key);
create table damage ("name" text primary key);
create table insurance ("name" text primary key);
create table relationship ("name" text primary key);

create table structure (
   accession_id text primary key,
   remediation_state text not null references remediation_state(name),
   distance text not null references distance(name),
   damage text not null references damage(name),
   insurance text not null references insurance(name),
   relationship text not null references relationship(name)
);

create table source_file (
   file_name text primary key,
   structure_id text not null references structure(accession_id),
   processed boolean not null default false,
   comments text
);   

