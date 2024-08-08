"""
This is init file for mail-server"""

#--------------------------------- IMPORTS -------------------------------------#
from os import system
from subprocess import run as foo
#-------------------------------------------------------------------------------#

#------------------------------- CONSTANTS -------------------------------------#
username = getenv("username")
green = "\033[0;32m"; red = "\033[31;49;1m"; blue = "\033[0;36m"; nocolor = "\\e[m"
#-------------------------------------------------------------------------------#


#------------------------------- Functions -------------------------------------#
def echo(arg: str):
    system(f'echo -e "{arg}"')

# Just modifying the subprocess.run() to give desired outputs.
def run(arg:str, no_sudo:bool=False, possible_warning=""): #NOTES: MAKE A REPEAT OPTION
    if no_sudo:
        arg = f"sudo -u {username} {arg}"
    try: 
        print(f"\n\nExecuting [{arg}]\n")
        foo(arg, shell=True, check=True) # This foo is subprocess.run()
    except Exception:
        echo(f"\n\n{red}While executing the command {nocolor}'{arg}'{red}, the above error occured.{nocolor}")
        proceed = (
                "\nWell, I can't possibly know what error you enountered. #"
                "If you don't want to proceed, the script will abort.\n"
                "Do you want to proceed? Yes or No: "
            )
        
        warning = f"But maybe... {possible_warning}. "
        proceed = proceed.replace("#", warning) if possible_warning else proceed.replace("#", possible_warning)

        proceed = yon(proceed)

        if not proceed: 
            print("Okay, aborted!")
            exit()
#-------------------------------------------------------------------------------#