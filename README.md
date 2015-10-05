e-Boks mailer
=============

Fetch unread "e-Boks" messages and mail them to yourself. 
Useful in a closed ecosystem, where you control your own mail server.

Usage:

    eboks-mailer.py /path/to/config.yaml

You need to configure this with your CPR#, password and activation key.

Python requirements:

- requests
- yaml
- BeautifulSoup (bs4)

Integration with Sieve filters
------------------------------

You can fetch messages automagically by triggering on the email sent from e-Boks.
Here is an example with a Sieve filter, using the `extprograms` plugin.

    require ["vnd.dovecot.execute"];

    if address :matches "From" "besked@advisering.e-boks.dk" {
        execute "eboks-mailer-trigger" "/home/<user>/.eboks.yaml";
        stop;
    }

Where `eboks-mailer-trigger` is a script in `/usr/lib/dovecot/sieve-execute`

    #!/bin/sh
    nohup /opt/eboks-mailer/eboks-mailer.py $1 &

And the master system config is something like (in `/etc/dovecot/dovecot.conf`)

    plugin {
      sieve_plugins = sieve_extprograms
      sieve_extensions = +vnd.dovecot.execute
      sieve_execute_bin_dir = /usr/lib/dovecot/sieve-execute
    }