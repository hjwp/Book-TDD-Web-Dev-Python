# Ultra-brief instructions for how to get a server

These are almost telegraphic in style, but I hope they're better than
nothing.

## Use Digital Ocean

I didn't want to make a specific recommendation in the book, but I'll make
one here. I like [Digital Ocean](https://m.do.co/c/876844cd6b2e).  Good value
for money, fast servers, and you can get a couple of months' worth of free
credit by following [my referral link](https://m.do.co/c/876844cd6b2e).


## Generate an SSH key

If you've never created one before, the command is

```bash
ssh-keygen
```

Just accept all the defaults if you really want to just get started in a hurry,
and no passphrase.

Later on, you'll want to re-create a key with a passphrase, but that means
you have to figure out how to save that passphrase in such a way that Fabric
won't ask for it later, and I don't have time to write instructions for that
now!

Make a note of your "public key"

```bash
cat ~/.ssh/id_rsa.pub
```



## Start a Droplet

A "droplet" is Digital Ocean's name for a server.  Pick the default Ubuntu,
the cheapest type, and whichever region is closest to you.

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

And you should be all set to follow the rest of the instructions in 
the manual deployment chapter


# Pull requests and suggestions accepted!

I literally threw these instructions together in 10 minutes flat, so I'm 
sure they could do with improvements.  Please send in suggestions, typos,
fixes, any common "gotchas" you ran into that you think I should mention.


