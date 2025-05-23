create table APIKeys (
    id serial primary key,
    email text not null,
    key text not null default md5(random()::text),
    description text,
    createdOn date default 'now'::date
);
