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

def yon(arg:str, assume=True, simple=True, default=False) -> bool:
    response = (input(arg)).lower()

    if default and response == "": return True

    if simple: 
        if "y" in response: return True
        elif "n" in response: return False
        else:
            if assume:
                print("Couldn't understand, so assuming No.")
                return False
            else: yon(arg, assume=assume, simple=simple, default=default)
            # I don't want to make this recursive, but well, I won't use this much.

    if response == "iall": return "iall"

    elif response == "sall": return "sall"

    elif response == "skip" or response == "s": return False

    elif response == "install" or response == "i": return True

    else:
        if assume:
            print("Couldn't understand, so assuming No.")
            return False
        else: yon(arg, assume=assume, simple=simple, default=default)
        # Read line 39

# Just modifying the subprocess.run() to give desired outputs.
def run(
    arg:str, 
    no_sudo:bool=False, 
    possible_warning:str=..., 
    capture_output:bool=False
    ) -> [str, str]: #NOTES: MAKE A REPEAT OPTION

    if no_sudo:
        arg = f"sudo -u {username} {arg}"

    print(f"\n\nExecuting [{arg}]\n")

    if capture_output:
        completedProcess = foo(arg, shell=True, capture_output=True) # This foo is subprocess.run()
        return completedProcess.stdout.decode(), completedProcess.stderr.decode()

    try: 
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