"""
This is init file for mail-server"""

#--------------------------------- IMPORTS -------------------------------------#
import pwd
from sys import exit
from pathlib import Path
from os import system, getenv
from subprocess import run as foo
#-------------------------------------------------------------------------------#

#------------------------------- CONSTANTS -------------------------------------#
username = getenv("username")
linuxDistribution = getenv("distro")
cwd = (Path(__file__).parent).absolute()
green = "\033[0;32m"; red = "\033[31;49;1m"; blue = "\033[0;36m"; nocolor = "\\e[m"
#-------------------------------------------------------------------------------#


#------------------------------- Functions -------------------------------------#
def echo(arg: str):
    system(f'echo "{arg}"')

def yon(arg:str, assume:bool=True, simple:bool=True, default:bool=False) -> bool:
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
    possible_warning:str="", 
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

def installPackage(packagename:str, fullname:str=..., check:bool=False) -> bool:
    if linuxDistribution == "Arch Linux":
        out, err =  run(f"pacman -Qi {packagename}", capture_output=True)
        installed = True if out else False

    elif linuxDistribution == "Debian/Ubuntu":
        out, err = run(f"dpkg -l {packagename}", capture_output=True)
        installed = packagename in out
    
    elif linuxDistribution == "Fedora":
        out, err = run(f"rpm -q {packagename}", capture_output=True)
        installed = True if out else False
    
    else: print("Something's fucked")
    
    if check: return installed

    if installed: return

    if fullname: name = fullname
    else: name = packagename

    echo(f"\n{green}Installing {name}{nocolor}")

    if linuxDistribution == "Arch Linux":
        run(f"pacman -S {packagename}")
    if linuxDistribution == "Debian/Ubuntu":
        run(f"apt-get install {packagename}")
    if linuxDistribution == "Fedora":
        run(f"dnf install {packagename}")


def verifyInput(i:str, keyword:str="") -> str:
    while True:
        value = input(i)
        if yon(f"Is {value} correct {keyword}? "):
            break
    return value

def postconf(arg:str):
    run(f"postconf -e '{arg}'")

def configuration(key:str, value:str, path:str, equal:str="="):
    with open(path, 'r') as file:
        lines = file.readlines()
    
    found = False

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith(key) and not value in line:
            lines[i] = f"{key} {equal} {value}\n"
            found = True
            break
    
    if not found:
        lines.append(f"{key} {equal} {value}\n")
    
    with open(path, 'w') as file:
        file.writelines(lines)
    
    if found:
        print(f"Updated: {key} {equal} {value} in {path}")
    else:
        print(f"Added: {key} {equal} {value} to {path}")
#-------------------------------------------------------------------------------#
