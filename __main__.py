#--------------------------------- IMPORTS -------------------------------------#
from os import getenv

from __init__ import echo, linuxDistribution
#-------------------------------------------------------------------------------#

#------------------------------- CONSTANTS -------------------------------------#
green = "\033[0;32m"; red = "\033[31;49;1m"; blue = "\033[0;36m"; nocolor = "\\e[m"
#-------------------------------------------------------------------------------#

#----------------------------- Script Start ---------------------------#
if linuxDistribution == "Arch Linux": 
    from archlinux import start
if linuxDistribution == "Debian/Ubuntu":
    from debian import start
if linuxDistribution == "Fedora":
    from fedora import start
#------------------------------ Script End ----------------------------#