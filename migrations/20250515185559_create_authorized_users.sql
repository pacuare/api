CREATE TABLE AuthorizedUsers (
    email TEXT NOT NULL PRIMARY KEY,
    fullAccess BOOLEAN DEFAULT FALSE
);
