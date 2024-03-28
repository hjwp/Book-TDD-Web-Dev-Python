# Ultra-brief instructions for how to get a Linux server

These instructions are meant as companion to the 
[deployment chapter of my book](https://www.obeythetestinggoat.com/book/chapter_11_ansible.html).
They're almost telegraphic in style, but I hope they're better than nothing!


## Use Digital Ocean

I didn't want to make a specific recommendation in the book itself, but I'll
make one here. I like [Digital Ocean](https://m.do.co/c/876844cd6b2e).
Good value for money, fast servers, and you can get a couple of months' worth
of free credit by following [my referral link](https://m.do.co/c/876844cd6b2e).


## Generate an SSH key

If you've never created one before, the command is

```bash
ssh-keygen
```

**NOTE** *If you're on Windows, you need to be using Git-Bash for `ssh-keygen`
and `ssh` to work. There's more info in the
[installation instructions chapter](https://www.obeythetestinggoat.com/book/pre-requisite-installations.html)*

Just accept all the defaults if you really want to just get started in a hurry,
and no passphrase.

Later on, you'll want to re-create a key with a passphrase for extra security,
but that means you have to figure out how to save that passphrase in such a way
that Fabric won't ask for it later, and I don't have time to write instructions
for that now!
<!--
CSANAD: We are no longer using Fabric
-->

Make a note of your "public key"

```bash
cat ~/.ssh/id_rsa.pub
```

More info on public key authentication [here](https://www.linode.com/docs/guides/use-public-key-authentication-with-ssh/)
and [here](https://docs.digitalocean.com/products/droplets/how-to/add-ssh-keys/)


## Start a Droplet

A "droplet" is Digital Ocean's name for a server.  Pick the default Ubuntu,
the cheapest type, and whichever region is closest to you. You won't need
access to the ancillary services that are available (Block storage, a VPC
network, IPv6, User-Data, Monitoring or Back-Ups)

* Choose **New SSH Key** and upload your public key from above

Make a note of your server's IP address once it's started


## Log in for the first time


```bash
ssh root@your-server-ip-address-here
```

It should just magically find your SSH key and log you in without any
need for a password.


## Create a non-root user

```bash
useradd -m -s /bin/bash elspeth # add user named elspeth 
# -m creates a home folder, -s sets elspeth to use bash by default
usermod -a -G sudo elspeth # add elspeth to the sudoers group
passwd elspeth # set password for elspeth
su - elspeth # switch-user to being elspeth!
```


## Add your public key to the non-root user as well.

* Copy your public key to your clipboard, and then


```bash
# as user elspeth
mkdir -p ~/.ssh
echo 'PASTE
YOUR
PUBLIC
KEY
HERE' >> ~/.ssh/authorized_keys
```

Now verify you can SSH in as elspeth from your laptop


```bash
ssh elspeth@your-server-ip-address-here
```

Also check you can use "sudo" as elspeth

```bash
sudo echo hi
```


## Map your domains to the server

There's one more thing you need to do in the book, which
is to map a domain name to your server's IP address.

If you don't already own a domain name you can use (you don't
have to use the *www.* subdomain, you could use *superlists.yourdomain.com*),
then you'll need to get on from a "domain registrar".  There are loads
out there, I quite like Gandi or the slightly-more-friendly (but
no 2FA) 123-reg.

If you want a free one there's [dot.tk](http://www.dot.tk).  Be aware
that their business model is based on ads, so there will be ads
all over your domain until you configure it.
<!-- CSANAD: first I thought this website was down, but then I realized my
browser blocked it. Unless there are no better alternatives, I don't think
recommending a services that don't use TLS is good. -->

Once you have a domain, you need to set up a couple of **A-records**, short
for Address Records, in
its DNS configuration, one for your "staging" subdomain and one for your
"live" subdomain.  Mine are *superlists.ottg.co.uk* and *staging.ottg.co.uk*
for example.
<!-- CSANAD: maybe I would mention associating IPv6 addresses are done in
AAAA records. I think it's a good practice to configure it too, and I
came across a few providers whose cheapest VPS packages were IPv6 only -->

*(tip: DNS changes take time to propagate, so if your domain doesn't
take you to the server straight away, you may need to wait.  Some registrars
will let you control this using a setting called "TTL")*.


And now you should be all set to follow the rest of the instructions in 
the manual deployment chapter


# Pull requests and suggestions accepted!

I literally threw these instructions together in 10 minutes flat, so I'm 
sure they could do with improvements.  Please send in suggestions, typos,
fixes, any common "gotchas" you ran into that you think I should mention.


