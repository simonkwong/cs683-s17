Add a database (e.g. MySQL) as the backend to your website that stores username and password. Build a login website so that you can demonstrate an SQL injection attack that will show all the usernames and passwords. (Hint: your website can login to the database as the admin to read username and password for the user.) This login website should act normally, e.g. this website should not be displaying the username and password in clear in a normal login process even for an admin account. Implement another version of the login website that prevents the attack you showed. (Hint: input sanitization) 





SQL INJECTIONS

username:		"; DROP TABLE users; --

username:		" OR hash LIKE "%
password:		" OR hash LIKE "%