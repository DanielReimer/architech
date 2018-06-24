#!/usr/bin/python3.6

import sys, os, argparse
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

def main():
    parser = argparse.ArgumentParser(description='Daniel\'s install script for Arch Linux')

    # arguments
    parser.add_argument("-u", "--uefi", help="Install systemd-boot with uefi support",
                        action="store_true")
    parser.add_argument("-l", "--legacy", help="Install grub2 with legacy bios support",
                        action="store_true")
    parser.add_argument("-r", "--root", help="Size of root partition (in GB) and /dev/$BLOCK",
                        type=str, nargs=2, required=True)
    parser.add_argument("-ho", "--home", help="Size of home partition (in GB) and /dev/$BLOCK",
                        type=str, nargs=2)


    args = parser.parse_args()

    # check internet connection
    if check_connectivity():
        print(INFO+"Internet connection was found")
    else:
        print(ERROR+"No internet connection was found")
        sys.exit(1)

    if args.uefi:
        partition_uefi(args.root, args.home)
    elif args.legacy:
        partition_legacy(args.root, args.home)
    else:
        if os.path.isdir("/sys/firmware/efi/efivars"):
            partition_uefi(args.root, args.home)
        else:
            partition_legacy(args.root, args.home)

    if os.system("timedatectl set-ntp true") != 0:
        print(WARNING+"Was unable to ensure system clock was accurate")

    sys.exit(0)


def check_connectivity():
    try:
        urllib.request.urlopen("https://www.google.com", timeout=2)
        return True
    except urllib.request.URLError:
        return False

def partition_uefi(root, home):
    print(INFO+"Using UEFI boot")


def partition_legacy(root, home):
    print(INFO+"Using legacy boot")

if __name__ == "__main__":
    main()
