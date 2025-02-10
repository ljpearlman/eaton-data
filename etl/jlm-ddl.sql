create schema jlm_raw;
set search_path = jlm_raw;

create table report (
   report_id serial primary key,
   report_name text unique not null
);

create table report_file (
   file_id serial primary key,
   file_name text unique not null,
   report_id integer references report(report_id)
);   

create table property_info (
   report_id integer not null references report(report_id),
   attr_name text not null,
   attr_value text,
   primary key(report_id, attr_name)
);

create table scope (
   report_id integer not null references report(report_id),
   attr_name text not null,
   attr_value text,
   primary key(report_id, attr_name)   
);

create table locations (
   report_id integer not null references report(report_id),
   location_name text not null,
   location_comments text,
   primary key(report_id, location_name)
);

create table area_inclusion (
   report_id integer not null references report(report_id),
   area_name text not null,
   area_included boolean,
   primary key(report_id, area_name)
);

create table samples (
   report_id integer not null references report(report_id),
   report_sample_id text not null,
   location_name text,
   material text,
   result text,
   primary key(report_id, report_sample_id)
);   
