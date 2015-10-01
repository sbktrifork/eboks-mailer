e-Boks mailer
=============

Fetch unread "e-Boks" messages and mail them to yourself. 
Useful in a closed ecosystem, where you control your own mail server.

Usage:

    eboks-mailer.py /path/to/config.yaml

You need to configure this with your CPR#, password and activation key.

Requirements:

- requests
- BeautifulSoup (bs4)

Integration with Sieve filters
------------------------------

An example usage with Dovecot


Example sieve filter:

    require ["vnd.dovecot.execute"];

    if address :matches "From" "besked@advisering.e-boks.dk" {
        execute "eboks-mailer-trigger /path/to/config.yaml";
        stop;
    }


