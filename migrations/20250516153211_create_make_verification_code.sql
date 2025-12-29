create function MakeVerificationCode (userEmail text, out result text) returns text language plpgsql as
$$ begin
    delete from logincodes
           where email = userEmail;
    insert into logincodes (email)
            values (userEmail)
            returning code into result;
end $$;
