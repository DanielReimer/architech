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

# load the config as global
with open('conf.json') as json_data:
    args = json.load(json_data)


def main():
    # check internet connection
    check_connectivity()

    if os.system("timedatectl set-ntp true") != 0:
        print(WARNING+"Was unable to ensure system clock was accurate")

    # partition and format drives
    if args["boot"] == "uefi":
        partition_uefi()
    elif args["boot"] == "legacy":
        partition_legacy()
    else:
        if os.path.isdir("/sys/firmware/efi/efivars"):
            args["boot"] = "uefi"
            partition_uefi()
        else:
            args["boot"] = "legacy"
            partition_legacy()

    partition_root()
    #partition_home()

    print(INFO+"Mounting partitions")
    os.system("mount "+args["root_blk"]+"2 /mnt")
    os.system("mkdir /mnt/boot")
    os.system("mount "+args["boot_blk"]+"1 /mnt/boot")

    # install packages
    print(INFO+"Installing packages with pacstrap")
    os.system("pacstrap /mnt "+args["pkgs"])

    print(INFO+"Generating fstab")
    os.system("genfstab -U /mnt >> /mnt/etc/fstab")

    # change root
    print(INFO+"Changing root")
    os.system("arch-chroot /mnt")
    os.chroot("/mnt")

    print(INFO+"Setting locale information")
    os.system("ln -sf /usr/share/zoneinfo/"+args["country"]+"/"+args["country"]+" /etc/localtime")
    os.system("hwclock --systohc")
    os.system("echo \"en_US.UTF-8 UTF-8\" >> /etc/locale.gen")
    os.system("locale.gen")
    os.system("echo \"LANG=en_US.UTF-8\" > /etc/locale.conf")

    set_hostname()

    os.system("mkinitcpio -p linux")

    os.system("passwd")
    os.system("reboot")

    sys.exit(0)


def check_connectivity():
    try:
        urllib.request.urlopen("https://www.google.com", timeout=3)
        print(INFO+"Internet connection was found")
    except urllib.request.URLError:
        print(ERROR+"No internet connection was found")
        sys.exit(1)

def partition_uefi():
    print(INFO+"Using UEFI boot")

    if os.system("echo -e \"g\nn\n1\n\n+512M\nt\n1\nw\n\" | fdisk "+args["boot_blk"]) != 0:
        print(ERROR+"Was unable to make uefi boot partition")
        sys.exit(1)

    if os.system("mkfs.fat -F32 "+args["boot_blk"]+"1") != 0:
        print(ERROR+"Was unable to format boot partition")
        sys.exit(1)

def partition_legacy():
    print(INFO+"Using legacy boot")
    if os.system("echo -e \"o\nn\np\n1\n\n+512M\na\nw\n\" | fdisk "+args["boot_blk"]) != 0:
        print(ERROR+"Was unable to make legacy boot partition")
        sys.exit(1)

    if os.system("mkfs.ext2 -F "+args["boot_blk"]+"1") != 0:
        print(ERROR+"Was unable to format boot partition")
        sys.exit(1)

def partition_root():
    # format size fdisk entry
    #if no entry for disk size, use entire disk
    size = "\n"
    if args["root_sz"] != "":
        size = "+"+args["root_sz"]+"M\n"

    if args["boot"] == "uefi":
        if os.system("echo -e \"n\n2\n\n"+size+"\nw\n\" | fdisk "+args["root_blk"]):
            print(ERROR+"Was unable to make a root partition")
            sys.exit(1)
    else:
        if os.system("echo -e \"n\np\n2\n\n"+size+"\nw\n\" | fdisk "+args["root_blk"]):
            print(ERROR+"Was unable to make a root partition")
            sys.exit(1)

    if os.system("mkfs.ext4 -F "+args["root_blk"]+"2") != 0:
        print(ERROR+"Was unable to format root partition")
        sys.exit(1)


def partition_home():
    return 0

def set_hostname():
    os.system("echo \""+args["hostname"]+"\" > /etc/hostname")
    hosts = """127.0.0.1	localhost
::1		localhost
127.0.1.1"""+args["hostname"]+".localdomain   "+args["hostname"]
    os.system("echo \""+hosts+"\" >> /etc/hosts")

if __name__ == "__main__":
    main()
