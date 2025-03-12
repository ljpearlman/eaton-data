set search_path = raw_data;

create table sample (
    report_file text not null references efru_data.report_file(file_name),
    sample_id text not null,
    lab_id text,
    collection_date timestamp,
    location text,
    analysis_method text,
    prep_method text,
    primary key (report_file, sample_id)
    )
    ;

create table result (
    report_file text not null,
    sample_id text not null,
    substance text not null,
    measurement text not null,
    units text,
    reporting_limit text,
    primary key (report_file, sample_id, substance),
    foreign key (report_file, sample_id) references sample(report_file, sample_id)
 );
    

    
