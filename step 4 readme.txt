

1. A cookie that the server returns is still replayable. It doesn't matter what is in the cookie, as long as the attacker can sniff it, they can replay it.

2. The way the website prevents this is by making sure the cookie is unique for every login and that the cookie has an expiration date of a day. When the user logs in, the cookie along with the timestamp of the cookie is sent to the server. The server takes the timestamp, verifies that it was within the expiration date. The server recreates the cookie with the given timestamp to check if they matched, if they match then the cookie isn't replayed and it is valid.

	Other options to implement is to use https, or encrypt all session data, or track cookie requests such that if it comes in from multiple ip's or devices, the cookie is invalid.