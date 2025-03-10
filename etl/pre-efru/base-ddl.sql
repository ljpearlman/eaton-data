create schema etl
set search_path = etl;

create table company (
   "name" text primary key
);

create table attribute_type (
   "name" text primary key
);

insert into attribute_type("name")
values ('inspection'), ('measurement');

create table attribute (
   attribute_name text,
   company_name text references company("name"),
   attribute_type text references attribute_type("name"),
   primary key (attribute_name, company_name)
);
