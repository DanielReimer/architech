#!/usr/bin/python3.6

import sys, os, json
import urllib.request, urllib.error

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

ERROR=bcolors.FAIL+"[ERROR]: "+bcolors.ENDC
OK=bcolors.OKGREEN+"[OK]: "+bcolors.ENDC
WARNING=bcolors.WARNING+"[WARNING]: "+bcolors.ENDC
INFO=bcolors.OKBLUE+"[INFO]: "+bcolors.ENDC

with open('conf.json') as json_data:
    args = json.load(json_data)


def main():
    if "garbage" in args:
        print("hi")

    # check internet connection
    if check_connectivity():
        print(INFO+"Internet connection was found")
    else:
        print(ERROR+"No internet connection was found")
        sys.exit(1)

    if os.system("timedatectl set-ntp true") != 0:
        print(WARNING+"Was unable to ensure system clock was accurate")

    # partition and format drives
    if args["boot"] == "uefi":
        partition_uefi()
    elif args["boot"] == "legacy":
        partition_legacy()
    else:
        if os.path.isdir("/sys/firmware/efi/efivars"):
            partition_uefi()
        else:
            partition_legacy()

    partition_root()
    partition_home()


    sys.exit(0)


def check_connectivity():
    try:
        urllib.request.urlopen("https://www.google.com", timeout=3)
        return True
    except urllib.request.URLError:
        return False

def partition_uefi():
    print(INFO+"Using UEFI boot")

    if os.system("echo -e \"g\nn\n1\n\n+512M\nt\n1\nw\" | fdisk "+args["boot_blk"]) != 0:
        print(ERROR+"Was unable to make uefi boot partition")
        sys.exit(1)

    if os.system("mkfs.fat -F32 "+args["boot_blk"]) != 0:
        print(ERROR+"Was unable to format boot partition")
        sys.exit(1)

def partition_legacy():
    print(INFO+"Using legacy boot")
    if os.system("echo -e \"o\nn\np\n1\n\n+512M\na\nw\" | fdisk "+args["boot_blk"]) != 0:
        print(ERROR+"Was unable to make legacy boot partition")
        sys.exit(1)

    if os.system("mkfs.ext2 "+args["boot_blk"]) != 0:
        print(ERROR+"Was unable to format boot partition")
        sys.exit(1)

def partition_root():
    # format size fdisk entry
    size = ""
    if args["root_sz"] != "":
        size = "+"+args["root_sz"]+"M"

    if args["boot"] == "uefi":
        if os.system("echo -e \"n\n\" | fdisk "+args["root_blk"]):
            print(ERROR+"Was unable to make a root partition")
            sys.exit(1)
    else:
        if os.system("echo -e \"n\np\n\" | fdisk "+args["root_blk"]):
            print(ERROR+"Was unable to make a root partition")
            sys.exit(1)

def partition_home():
    print("hi")

if __name__ == "__main__":
    main()
