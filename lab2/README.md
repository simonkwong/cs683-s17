# 	Step 2. Cookies (by 2/3)

https://github.com/simonkwong/cs683-s17


In Packet #41 You can Clearly See How The Cookie Is Being Exchanged In The Header. Once The Login Info Is Inputted, You Can See The Info Being Passed In From The HTML Form All In PlainText.

In Packet #49 Is Where You Can Still See The 90 Day Life Set-Cookie username-simonkwong

In Packet #71 The Cookie Is Still Set Even After Closing and Reopening The Browser

In Packet #116 The Cookie Is Removed From The Browser And Therefore The User Is Sent Back From The Home Page To The Main Welcome Page Requesting For A Login

I'm Using the Flask web server and also coupled with MySQL. I have a landing page that welcomes the user, requesting to either register for an account or login. When a use registers, it adds the user, creates a random generated salt, hashes the password with the salt and adds that to the database. When logging in, it takes the given users password along with the stored salt, hashes that and compares it to the stored hash, if they match, the user is granted access to their homepage. If a user attempts to access the homepage without appropriate credentials they are redirected to login or register. With a successful login, a cookie is set in the browser that lasts 90 days. Once the cookie is set, the user is allowed to access the home page without logging in again, they may close the browser and reopen it, or also use multiple tabs. Once the cookie is removed, they lose access to the private home page and is asked to login again.

By Examining Facebook Cookies, You can See That sites that utilize facebook's web services send a cookie containing facebook user's information that was stored on the browser. Packets such as 4867, 4956, 4962, and a handful of others all contain facebook cookie information. Which is awful, cause someone sitting a couple feet away could capture those packets, go to a browser and replay the cookies, and voila they have access to my facebook account without be knowing. You can also see the expirations of the cookies, and they don't expire any time soon. Just by looking at the cookie you probably wouldn't notice anything, until you replay the cookie and visit the site and realize you have access without logging in.


I used the open source SSL library for openssl.
Generate a private key
openssl genrsa -des3 -out server.key 1024
Generate a CSR
openssl req -new -key server.key -out server.csr
Generate self signed certificate
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
Backup your key:
cp server.key server.key.org
Strip out the password: (So that it doesn't require a PEM key for login)
openssl rsa -in server.key.org -out server.key

Then I added it to Flasks ssl context. and visited https://localhost:8080/

Upon reviewing the cookies, 
I see cookies with Set-Cookie: ..... secure; httpOnly;


##### Implement a login page that uses username/password. Do not use htaccess, and do not store the plaintext of the password on the server. Any passwords should be hashed before being stored. You don't have to use a database to store passwords. You may use salt, but it is not required. Set a permanent cookie once login is sucessful, i.e. the cookie does not expire. Implement a private page that requires this cookie, i.e. a page that only logged-in users can see. You may use PHP or javascript to set the cookie. (The university offers free training on Apache+PHP+MySQL at Lynda.com. Login to USF Connect, click on Learning Technologies, and then click on Lynda.com. You can search for Apache.)
##### From the client web browser, visit your login page, and capture the packets to show how the username, password, and cookie is exchanged between the website to the browser. Close your web browser, visit the private page that requires cookie again, and capture the packets to show how the cookie is sent from your browser to the website. Clear the cookie in the web browser, and then visit the private page again, while capturing the packets. Your website should deny access to this page. Submit the source code of your login and private pages with the pcap file and README that explains how you implemented login and private pages.
##### Read the article Logging out of facebook is not enough. https://www.nikcub.com/posts/logging-out-of-facebook-is-not-enough/ Create a Facebook account if you don't have one. Start packet capture. Login, logout, and visit 3rd-party websites (non-Facebook websites) with Like button such as this. http://www.dictionary.com/wordoftheday/ Submit the pcap file and show which packets send the Facebook cookies to Facebook when your browser visits the 3rd-party websites and README that explains what you can learn from these Facebook Cookies about your account.
##### Add SSL to your website to support https for username/password login. Do not use htaccess, but implement a login page. Use Wireshark to verify that the passwords are not visible. You may use Apache-SSL. Submit the source code of your login page if it has changed and a README. The README should explain how you added SSL, and also whether the cookie is visible or not.