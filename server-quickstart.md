# Ultra-brief instructions for how to get a Linux server

These instructions are meant as companion to the 
[server prep chapter of my book](https://www.obeythetestinggoat.com/book/chapter_11_server_prep.html).
They're almost telegraphic in style, but I hope they're better than nothing!


## Use Digital Ocean

I didn't want to make a specific recommendation in the book itself,
but I'll make one here.
I like [Digital Ocean](https://m.do.co/c/876844cd6b2e).
Good value for money, fast servers,
and you can get a couple of months' worth of free credit
by following [my referral link](https://m.do.co/c/876844cd6b2e).


## Generate an SSH key

SSH aka "secure shell" is a protocol for running a terminal
session on a remote server, across the network.
It involves authentication, as you might expect,
and different types of it.
You can use usernames and passwords,
but public/private key authentication is more convenient,
and (as always, arguably) more secure.

If you've never created one before, the command is

```bash
ssh-keygen
```

**NOTE** _If you're on Windows,
you need to be using Git-Bash for `ssh-keygen` and `ssh` to work.
There's more info in the
[installation instructions chapter](https://www.obeythetestinggoat.com/book/pre-requisite-installations.html)_

Just accept all the defaults if you really want to just get started in a hurry,
and no passphrase.

Later on, you'll want to re-create a key with a passphrase for extra security,
but that means you have to figure out how to save that passphrase in such a way
that Ansible won't ask for it later, and I don't have time to write instructions
for that now!

Make a note of your "public key"

```bash
cat ~/.ssh/id_rsa.pub
```

More info on public key authentication [here](https://www.linode.com/docs/guides/use-public-key-authentication-with-ssh/)
and [here](https://docs.digitalocean.com/products/droplets/how-to/add-ssh-keys/)


## Start a Server aka VM aka Droplet

A "droplet" is Digital Ocean's name for a server.
Pick the default Ubuntu, the cheapest type,
and whichever region is closest to you.
You won't need access to the ancillary services that are available
(Block storage, a VPC network, IPv6, User-Data, Monitoring, Back-Ups, etc,
don't worry about those)

* Choose **New SSH Key** and upload your public key from above

Make a note of your server's IP address once it's started


## Log in for the first time


```bash
ssh root@your-server-ip-address-here
```

It should just magically find your SSH key and log you in
without any need for a password.  Hooray!


## Create a non-root user

It's good security practice to avoid using the root user directly.
Let's create a non-root user with super-user ("sudo") privileges,
a bit like you have on your own machine.

```bash
useradd -m -s /bin/bash elspeth # add user named elspeth 
# -m creates a home folder, -s sets elspeth to use bash by default

usermod -a -G sudo elspeth # add elspeth to the sudoers group

# allow elspeth to sudo without retyping password
echo 'elspeth ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/elspeth

 # set password for elspeth (you'll need to type one in)
passwd elspeth

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

Now log out from the server,
and verify you can SSH in as elspeth from your laptop


```bash
ssh elspeth@your-server-ip-address-here
```

Also check you can use "sudo" as elspeth

```bash
sudo echo hi
```


## Registering a domain name

There's one more thing you need to do in the book,
which is to map a domain name to your server's IP address.

If you don't already own a domain name you can use
(you don't have to use the *www.* subdomain, you could use *superlists.yourdomain.com*),
then you'll need to get one from a "domain registrar".
There are loads out there, I quite like Gandi or the slightly-more-friendly 123-reg.

There aren't any registrars offering free domain names any more,
but the cheapest registrar I've found is https://www.ionos.co.uk/,
where last I checked you could get a domain for one pound, like $1.50, for a year.
But I haven't used them myself personally.


# Pull requests and suggestions accepted!

I literally threw these instructions together in 10 minutes flat, so I'm 
sure they could do with improvements.  Please send in suggestions, typos,
fixes, any common "gotchas" you ran into that you think I should mention.


