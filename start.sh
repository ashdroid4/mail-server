#!/bin/bash

## Checking if the user is sudo. We don't want this script to be run with sudo.
if [[ $EUID -eq 0 ]]; then
    echo "\033[31;49;1mThis script should not be run with sudo.\\e[m"
    exit 1
fi

# Function to detect the Linux distribution.
detect_distro() {
    if command -v apt-get &> /dev/null; then
        distro="Debian/Ubuntu"
    elif command -v dnf &> /dev/null; then
        distro="Fedora"
    elif command -v pacman &> /dev/null; then
        distro="Arch Linux"
    else
        echo -e "\033[31;49;1mYour linux distribution is not supported by this script. EXITING!\\e[m"
        exit 1
    fi

    export distro
    echo -e "\033[0;36mDetected Linux Distribution:\033[0;36m $distro\\e[m"
}

detect_distro

# Let's install/update Python.
install_python() {
    case "$distro" in
        "Debian/Ubuntu")
            sudo apt-get update
            sudo apt-get install python3
            ;;
        "Fedora")
            sudo dnf install python3
            ;;
        "Arch Linux")
            sudo pacman -Sy python
            ;;
        *)
    esac
}

echo -e "\033[0;32mUpdating repositories and installing/updating Python.\\e[m"

install_python

## Changing to the directory where the file resides.
cd "$( dirname "${BASH_SOURCE[0]}" )"

## Now it is the time to set one environment variable.
export username=$(whoami)


## Starting the main script.
sudo -E python3 .
