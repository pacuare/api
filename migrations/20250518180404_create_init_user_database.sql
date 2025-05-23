create function InitUserDatabase(databaseUrlBase text, databaseData text, email text) returns text language plpgsql as
$$ declare
    databaseName text := GetUserDatabase(email);
    userUrl text := databaseUrlBase || '/' || databaseName;
    dataUrl text := databaseUrlBase || '/' || databaseData;
    _tmp record;
begin
    select dblink_connect(databaseName, userUrl) into _tmp;
    select dblink_exec(databaseName, 'create extension if not exists dblink') into _tmp;
    select dblink_exec(databaseName, '
        create table pacuare_raw
            as select *
               from dblink(''' || dataUrl || ''', ''
                select * from pacuare_raw
               '')
               as t1(
                id text,
                date text,
                year integer,
                time text,
                location double precision,
                weather text,
                turtle text,
                turtle_species text,
                turtle_processed text,
                turtle_activity    text,
                nest_activity      text,
                relocation_reason  text,
                zone               text,
                hour_first_egg     text,
                hour_final_egg     text,
                nest_depth         text,
                nest_loss          text,
                ccw_acc            text,
                ccl_lcc            text,
                turtle_id          text,
                neophyte           text,
                bank_height        text,
                climbed_bank       text,
                injuries           text,
                observations       text,
                hatch_date         text,
                hatch_hour         text,
                exhumation_date    text,
                infertile_eggs     text,
                fertile_eggs       text,
                hatched_eggs       text,
                unhatched_eggs     text
               )') into _tmp;
    select dblink_disconnect(databaseName) into _tmp;

    return databaseName;
end $$
