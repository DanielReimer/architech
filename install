#!/usr/bin/python3.6

# Copyright (c) 2018 Daniel Reimer

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

def validate_args():
    return 0

def main():
    validate_args()

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

    print(INFO+"Setting locale information")
    os.system("ln -sf /mnt/usr/share/zoneinfo/"+args["country"]+"/"+args["country"]+" /mnt/etc/localtime")
    os.system("arch-chroot /mnt hwclock --systohc")
    os.system("echo \"en_US.UTF-8 UTF-8\" >> /mnt/etc/locale-gen")
    os.system("arch-chroot /mnt locale.gen")
    os.system("echo \"LANG=en_US.UTF-8\" > /mnt/etc/locale.conf")

    print(INFO+"Setting hostname")
    set_hostname()

    os.system("arch-chroot /mnt mkinitcpio -p linux")

    print(INFO+"Installing bootloader")
    install_bootloader()

    print(INFO+"Configuring users")
    os.system("arch-chroot /mnt useradd --create-home "+args["username"])
    os.system("echo \"%wheel ALL=(ALL) ALL\" >> /mnt/etc/sudoers")
    os.system("arch-chroot /mnt gpasswd -a "+args["username"]+" "+args["group"])

    print(INFO+"Installing the desktop environment")
    install_desktop_environment()

    print(INFO+"Set root password")
    os.system("arch-chroot /mnt passwd")

    print(INFO+"Set password for: "+args["username"])
    os.system("arch-chroot /mnt passwd "+args["username"])

    print(INFO+"Rebooting...")
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
    os.system("echo \""+args["hostname"]+"\" > /mnt/etc/hostname")
    hosts = """127.0.0.1	localhost
::1		localhost
127.0.1.1 """+args["hostname"]+".localdomain   "+args["hostname"]
    os.system("echo \""+hosts+"\" >> /mnt/etc/hosts")

def install_bootloader():
    os.system("arch-chroot /mnt pacman --noconfirm -Sy grub")
    if args["boot"] == "uefi":
        os.system("arch-chroot /mnt pacman --noconfirm -Sy efibootmgr")
        os.system("arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB")
    elif args["boot"] == "legacy":
        os.system("arch-chroot /mnt grub-install --target=i386-pc "+args["boot_blk"])
    os.system("arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg")

def install_desktop_environment():
    os.system("arch-chroot /mnt pacman --noconfirm -Sy archlinux-keyring")
    os.system("arch-chroot /mnt pacman --noconfirm -Sy xorg-server xorg-xinit i3")
    os.system("cp /mnt/etc/X11/xinit/xinitrc /mnt/home/"+args["username"]+"/.xinitrc")
    os.system("head -n -5 /mnt/home/"+args["username"]+"/.xinitrc")
    os.system("echo \"exec i3\" >> /mnt/home/"+args["username"]+"/.xinitrc")
    autostart = """if [[ ! $DISPLAY && $XDG_VTNR -eq 1 ]]; then
  exec startx
fi"""
    os.system("echo \""+autostart+"\" >> /mnt/home/"+args["username"]+"/.bash_profile")

if __name__ == "__main__":
    main()
