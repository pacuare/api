create procedure DeleteExpiredKeys()
language sql
as $$
    delete from APIKeys where createdOn < ('now'::date - '30 days'::interval);
$$;
