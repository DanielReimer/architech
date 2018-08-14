# Architech

Copyright (c) 2018 Daniel Reimer

## Overview

An Arch Linux installer. The main goal for this project is to be able to install and configure a new Arch install consistently accross machines. By having a simple config file, it is easy to replacate configurations.

## Usuage

After booting into the Arch Linux liveCD, download the files

`root@archiso ~ # curl architech.sh | bash && cd architech`

Open the file `conf.json` file with your favorite text editor and make configurations

### Configuration Options

* hostname	      - The hostname that will be assigned
* boot       	      - Partitioning scheme for type of boot. `uefi`, `legacy` or blank for automatic
* bool_blk   	      - The block device the bootloader will be installed on
* root_blk   	      - The block device the root partition will be installed on
* root_sz    	      - Size of root partition
* home_blk   	      - The block device the home partition will be installed on
* pkgs       	      - List of packages to be installed
* conutry             - Country
* city		      - City
* username	      - Username
* group		      - Groups for the user to be in (wheel is sudo group by default)
* desktop_environment - Only option right now is `i3`

When completed, run `./architech.sh` to start the installation process

## Contributing

Clone the repository
`git clone git@github.com:DanielReimer/architech.git`

## License

Architech is licensed under the MIT license. See the `LICENSE` file in the project for a copy of the license.

## Contact

For issues or missing features, please submit an issue ticket through GitHiub

Email: daniel.k.reimer97@gmail.com