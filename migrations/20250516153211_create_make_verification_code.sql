create function MakeVerificationCode (userEmail text, out result text) returns text language plpgsql as
$$ begin
    delete from LoginCodes
           where email = userEmail;
    insert into LoginCodes (email)
            values (userEmail)
            returning code into result;
end $$;
