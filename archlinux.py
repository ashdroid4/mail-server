"""This will setup mail-server in Arch Linux based distributions"""

#--------------------------------- IMPORTS -------------------------------------#
from __init__ import echo, run, yon, installPackage, postconf, configuration, verifyInput

#-------------------------------------------------------------------------------#

#------------------------------- CONSTANTS -------------------------------------#
green = "\033[0;32m"; red = "\033[31;49;1m"; blue = "\033[0;36m"; nocolor = "\\e[m"
#-------------------------------------------------------------------------------#

#------------------------------- Functions -------------------------------------#

#-------------------------------------------------------------------------------#

#----------------------------- Script Start ---------------------------#

# Let's update package database and upgrade system.
echo(f"{green}Upgrading system...{nocolor}")
run("pacman -Syu")

# Let's install Postfix.
installPackage("postfix", fullname="Postfix")

# Let's configure Postfix.
echo(f"\n{blue}You will be asked some important Postfix configurations next.\n{nocolor}")

echo("Type your domain name. For example: domain.com\n")

domain = verifyInput("Enter your domain: ")

postconf(f"myhostname = mail.{domain}")
postconf(f"mydomain = {domain}")
postconf(f"myorigin = $mydomain")
postconf(f"inet_interfaces = all")
postconf(f"mydestination = $myhostname, localhost.$mydomain, localhost")

#sudo grep -q '^Socket' /etc/opendkim.conf || echo 'Socket = inet:12301@localhost' | sudo tee -a /etc/opendkim.conf

# Let's install Dovcot
installPackage("dovecot", fullname="Dovecot")

# Let's configure Dovecot
echo(f"{green}\nConfiguring Dovecot to listen to emails.{nocolor}\n")

run("cp -r -f /usr/share/doc/dovecot/example-config/* /etc/dovecot/")

configuration("listen", "*", "/etc/dovecot/dovecot.conf")

configuration("disable_plaintext_auth", "yes", "/etc/dovecot/conf.d/10-auth.conf")
configuration("auth_mechanisms", "plain login", "/etc/dovecot/conf.d/10-auth.conf")
configuration("!include", "auth-system.conf.ext", "/etc/dovecot/conf.d/10-auth.conf", equal=False)

configuration("mail_location", "maildir:~/Maildir", "/etc/dovecot/conf.d/10-mail.conf")

with open("/etc/dovecot/conf.d/10-master.conf", "r+") as file:
    inside = file.read()
    inside.append(
        """
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0666
    user = postfix
    group = postfix
  }
}
        """
    )

# Let's configure SSL 
echo(f"\n{green}Let's configure SSL with Let's SSL.\n{nocolor}")
## Installing certbot
installPackage("certbot")

run(f"certbot certonly --standalone -d mail.{domain}")


#------------------------------ Script End ----------------------------#