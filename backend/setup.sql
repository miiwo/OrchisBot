create database if not exists sierro_shop;
use sierro_shop;

create table if not exists sparks (
    id bigint unsigned not null unique,
    crystals int unsigned not null,
    tenpull int unsigned not null,
    onepull int unsigned not null,
    primary key (id)
);

create user orchisbot@localhost identified by orchidnotorchis;
grant select, insert, update on sparks to orchisbot@localhost;