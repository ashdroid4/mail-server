"""This will setup mail-server in Arch Linux based distributions"""

#--------------------------------- IMPORTS -------------------------------------#
from __init__ import echo, run, installPackage, postconf, configuration, verifyInput, username, pwd, Path
#-------------------------------------------------------------------------------#

#------------------------------- CONSTANTS -------------------------------------#
green = "\033[0;32m"; red = "\033[31;49;1m"; blue = "\033[0;36m"; nocolor = "\\e[m"
#-------------------------------------------------------------------------------#

#------------------------------- Functions -------------------------------------#

#-------------------------------------------------------------------------------#

#----------------------------- Script Start ---------------------------#

# Let's install some packages.
echo(f"{green}Starting...{nocolor}")
installPackage("postfix", fullname="Postfix")
installPackage("dovecot-core")
installPackage("dovecot-imapd")
installPackage("dovecot-pop3d")
installPackage("opendkim", fullname="OpenDKIM")
installPackage("opendkim-tools")
installPackage("systemctl")
installPackage("openssl", fullname="OpenSSL")

# Getting to know you.
echo("Type your domain name. For example: domain.com\n")

domain = verifyInput("Enter your domain: ")

# Let's configure the MailBox
print(f"\nTell the username you want to use for the email. For example: username@{domain}")

domainUsername = verifyInput("Username: ")
if not domainUsername == username:
    try:
        pwd.getpwnam(domainUsername)
        print("Okay got it!")
        print(f"Your email password is the same as your useraccount {domainUsername} "
        f"To change type 'passwd {username}')
    except KeyError:
        run(f"useradd -m /bin/false {domainUsername}")
        print("\nYOU WILL BE PROMPTED WITH PASSWORD FOR YOUR EMAIL.")
        run(f"passwd {domainUsername}")
        print(f"\nIf you want to change the password then type 'passwd {domainUsername}'")
else:
    print(f"\nYour email password is the same as your useraccount {username} " 
    f"To change type 'passwd {username}'")

out, err = run(f"sudo -u {domainUsername} cd Maildir", capture_output=True)
if err:
    run(f"mkdir /home/{domainUsername}/Maildir")
    run(f"chmod -R 700 /home/{domainUsername}/Maildir")
    run(f"sudo chown -R {domainUsername}:{domainUsername} /home/{domainUsername}/Maildir")

# Let's configure Postfix.
postconf(f"myhostname = mail.{domain}")
postconf(f"mydomain = {domain}")
postconf(f"myorigin = $mydomain")
postconf(f"inet_interfaces = all")
postconf(f"mydestination = $myhostname, localhost.$mydomain, localhost")
postconf(f"home_mailbox = Maildir/")

# Let's setup dovecote to listen to emails.
echo(f"\n{green}Setting up Dovecot to listen to emails.{nocolor}\n")

## Let's configure Dovecot
echo(f"{green}\nConfiguring Dovecot to listen to emails.{nocolor}\n")

out, err = run("ls /etc/dovecot/dovecot.conf", capture_output=True)

if err:
    run("cp -r -f /usr/share/doc/dovecot/example-config/* /etc/dovecot/")

configuration("listen", "*", "/etc/dovecot/dovecot.conf")

configuration("disable_plaintext_auth", "yes", "/etc/dovecot/conf.d/10-auth.conf")
configuration("auth_mechanisms", "plain login", "/etc/dovecot/conf.d/10-auth.conf")
configuration("!include", "auth-system.conf.ext", "/etc/dovecot/conf.d/10-auth.conf", equal=" ")
configuration("passdb", "{driver = pam}", "/etc/dovecot/conf.d/10-auth.conf", equal=" ")
configuration("userdb", "{driver = passwd}", "/etc/dovecot/conf.d/10-auth.conf", equal=" ")

configuration("mail_location", "maildir:~/Maildir", "/etc/dovecot/conf.d/10-mail.conf")

with open("/etc/dovecot/conf.d/10-master.conf", "r+") as file:
    conf = """
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0666
    user = postfix
    group = postfix
  }
}
    """
    inside = file.read()
    if conf not in inside: inside += conf
    file.write(inside)

## Configuring Postfix to use Dovecot for SASL Authentication
postconf("smtpd_sasl_type = dovecot")
postconf("smtpd_sasl_path = private/auth")
postconf("smtpd_sasl_auth_enable = yes")
postconf("smtpd_tls_auth_only = yes")
postconf("smtpd_recipient_restrictions = "
         "permit_sasl_authenticated, "
         "permit_mynetworks, "
         "reject_unauth_destination")
postconf("smtpd_sasl_security_options = noanonymous")

# Let's configure SSL 
if not Path("/etc/ssl/certs/dovecot.pem").exists():
    echo(f"\n{green}Let's configure SSL.\n{nocolor}")

## Configuring OpenSSL
    run("mkdir -p /etc/ssl/certs")
    run("mkdir -p /etc/ssl/private")

    run("openssl req -new -x509 -days 365 -nodes " +
    "-out /etc/ssl/certs/dovecot.pem -keyout /etc/ssl/private/dovecot.key")

## Setting appropriate permissions
    run("chmod 644 /etc/ssl/certs/dovecot.pem")
    run("chmod 600 /etc/ssl/private/dovecot.key")

## Configuring Dovecot to Use the SSL Certificate
    echo(f"\n{blue}Now, let's configure Dovecot to use the certificate.{nocolor}")

    configuration("ssl", "yes", "/etc/dovecot/conf.d/10-ssl.conf")
    configuration("ssl_cert", "</etc/ssl/certs/dovecot.pem", "/etc/dovecot/conf.d/10-ssl.conf")
    configuration("ssl_key", "</etc/ssl/private/dovecot.key", "/etc/dovecot/conf.d/10-ssl.conf")

## Configuring postfix to use the certificates.
    echo(f"\n{blue}Now, let's configure Postfix to use the certificate.{nocolor}")

    run(f"postconf -e 'smtpd_tls_cert_file=/etc/ssl/certs/dovecot.pem'")
    run(f"postconf -e 'smtpd_tls_key_file=/etc/ssl/private/dovecot.key'")
    run("postconf -e 'smtpd_use_tls=yes'")

# Configuring Postfix to enable ports 587 and 465
with open("/etc/postfix/master.cf", "r+") as file:
    conf = """
submission inet n - y - - smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_security_level=encrypt
  -o smtpd_sasl_auth_enable=yes

smtps inet n - y - - smtpd
  -o syslog_name=postfix/smtps
  -o smtpd_tls_wrappermode=yes
  -o smtpd_sasl_auth_enable=yes
"""

    inside = file.read()
    if conf not in inside: inside += conf
    echo(f"\n{blue}Configuring Postfix to enable ports 587 and 465.{nocolor}\n")
    file.write(inside)

# Setting up DKIM
echo(f"\n{green}Setting up DKIM\n{nocolor}")

## Configuring OpenDKIM
openDKIMConf = {
    "AutoRestart": "Yes",
    "AutoRestartRate": "10/1h",
    "Syslog": "Yes",
    "SyslogSuccess": "Yes",
    "LogWhy": "Yes",
    "Canonicalization ": "relaxed/simple",
    "ExternalIgnoreList": "refile:/etc/opendkim/TrustedHosts",
    "InternalHosts": "refile:/etc/opendkim/TrustedHosts",
    "KeyTable": "refile:/etc/opendkim/KeyTable",
    "SigningTable": "refile:/etc/opendkim/SigningTable",
    "Mode": "sv",
    "PidFile": "/var/run/opendkim/opendkim.pid",
    "SignatureAlgorithm": "rsa-sha256",
    "UserID": "opendkim:opendkim",
    "Socket": "inet:12301@localhost",
}

out, err = run("ls /etc/opendkim/opendkim.conf", capture_output=True)

if err:
    run("cp -f /usr/share/doc/opendkim/opendkim.conf.sample /etc/opendkim/opendkim.conf")

for key in openDKIMConf:
    configuration(key, openDKIMConf[key], "/etc/opendkim/opendkim.conf", equal="    ")

## Generating Keys
echo("Generating DKIM keys.")

run(f"mkdir -p /etc/opendkim/keys/{domain}")
run(f"opendkim-genkey -s default -d {domain} -D /etc/opendkim/keys/{domain}")
run("chown -R opendkim:opendkim /etc/opendkim/keys")
run(f"chmod go-rw /etc/opendkim/keys/{domain}/default.private")

## Configuring Tables
echo("Configuring DKIM Tables.")

with open("/etc/opendkim/KeyTable", "w+") as file:
    file.write(
f"default._domainkey.{domain} {domain}:default:/etc/opendkim/keys/{domain}/default.private"
    )

with open("/etc/opendkim/SigningTable", "w+") as file:
    file.write(
f"*@{domain} default._domainkey.{domain}"
    )

with open("/etc/opendkim/TrustedHosts", "w+") as file:
    file.write(f"""
127.0.0.1
localhost
{domain}
    """)

## Configuring Postfix to use OpenDKIM
echo(f"{blue}Configuring Postfix to use OpenDKIM\n{nocolor}")

run("postconf -e 'milter_default_action = accept'")
run("postconf -e 'milter_protocol = 6'")
run("postconf -e 'smtpd_milters = inet:localhost:12301'")
run("postconf -e 'non_smtpd_milters = inet:localhost:12301'")

# Let's restart and enable all the services
echo(f"\n{green}Starting your mail server.{nocolor}\n")
run("systemctl enable postfix")
run("systemctl enable dovecot")
run("systemctl enable opendkim")
run("systemctl restart postfix")
run("systemctl restart dovecot")
run("systemctl restart opendkim")

echo(f"""\n\n
Setup the DNS records:

1. A RECORD
    Type -> A
    Name -> mail.{domain}
    Content -> Your IP address

2. SPF RECORD:
    Type -> TXT
    Name -> @
    Content -> v=spf1 mx ~all 

3. DKIM RECORD:
    Type -> TXT
    Name -> default._domainkey
    Content -> get it from /etc/opendkim/keys/{domain}/default.txt

4. DMARC RECORD
    Type -> TXT
    Name -> _dmarc
    Content -> "v=DMARC1; p=none; rua=mailto:postmaster@{domain}"

5. MX RECORD
    Type -> MX
    Name -> @
    Content -> mail.{domain}
    Priority -> 10
    """)

start = True
#------------------------------ Script End ----------------------------#
