[![PyPI version](https://badge.fury.io/py/liewa.svg)](https://badge.fury.io/py/liewa)
![Linux](https://svgshare.com/i/Zhy.svg)
![macOS](https://svgshare.com/i/ZjP.svg)
![Windows](https://svgshare.com/i/ZhY.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

# Live-Earth-Wallpapers aka liewa
Set your Desktop background to near realtime picures of the earth.
Supports all known **geostationary** satellites, high resolution **sentinel** images, Nasa **Solar Dynamics Observatory** Images and Nasa astronomy picture of the day (Apod)! For Linux, Windows and MacOs!

***
## Examples
<!-- ![alt text](examples/config1.png) -->
![](https://github.com/lennart-rth/Live-Earth-Wallpapers/blob/main/examples/config1.png)
*Example Output of the config1.yml file. Use this by passing config1 to -o flag.*
<!-- ![alt text](examples/config2.png) -->
![](https://github.com/lennart-rth/Live-Earth-Wallpapers/blob/main/examples/config2.png)
*Example Output of the config2.yml file. Use this by passing config2 to -o flag.*
<!-- ![alt text](examples/config3.png) -->
![](https://github.com/lennart-rth/Live-Earth-Wallpapers/blob/main/examples/config3.png)
*Example Output of the config3.yml file. Use this by passing config3 to -o flag.*
<!-- ![alt text](examples/caribic.png) -->
![](https://github.com/lennart-rth/Live-Earth-Wallpapers/blob/main/examples/caribic.png)
*Example Output of the Sentinel satellite. Learn how to generate custom images for your location at the [Wiki Page](https://github.com/lennart-rth/Live-Earth-Wallpapers/wiki)*
<!-- ![alt text](examples/arctic.png) -->
![](https://github.com/lennart-rth/Live-Earth-Wallpapers/blob/main/examples/arctic.png)
*Example Output of the Sentinel satellite. Learn how to generate custom images for your location at the [Wiki Page](https://github.com/lennart-rth/Live-Earth-Wallpapers/wiki)*
<!-- ![alt text](examples/desert.png) -->
![](https://github.com/lennart-rth/Live-Earth-Wallpapers/blob/main/examples/desert.png)
*Example Output of the Sentinel satellite. Learn how to generate custom images for your location at the [Wiki Page](https://github.com/lennart-rth/Live-Earth-Wallpapers/wiki)*
<!-- ![alt text](examples/apod-cover.png) -->
![](https://github.com/lennart-rth/Live-Earth-Wallpapers/blob/main/examples/apod-cover.png)
*Example Output for astronomy picture of the day feed (apod)(2022 November 15).*
### Build images to your needs by writing your own config.yml file or using the GUI.
### Read more on the [Wiki Page](https://github.com/lennart-rth/Live-Earth-Wallpapers/wiki).
***
## Installation

**You need Python installed and added to your System-path-variable!**

### Using PyPi (Linux,MacOs)
1. Install liewa-software from [pypi Package]()
2. execute command line Interface by `liewa-cli` or the Gui by `liewa-gui`.

### Windows
1. Download the `liewaInstaller.exe` from [Releases Page](https://github.com/lennart-rth/Live-Earth-Wallpapers/releases) and execute the GUI.
2. If the desktopimage hasn´t changed, take a look at the [Known bugs](##Known-Bugs) section.

### Linux
1. Download the `liewa.deb` file from [Releases Page](https://github.com/lennart-rth/Live-Earth-Wallpapers/releases).
2. Execute `sudo dpkg -i liewa.deb`.

### MacOS
1. Download the `liewa.dmg` drive from the [Releases Page](https://github.com/lennart-rth/Live-Earth-Wallpapers/releases).
2. Drag and Drop the liewa software into the Program Folders.

### For detailed userguide, read the [wiki page](https://github.com/lennart-rth/Live-Earth-Wallpapers/wiki).

## Usage
### Script Parameters:
| short | long     | type   | default                              | help                                                                 |
|-------|----------|--------|--------------------------------------|----------------------------------------------------------------------|
| -c    | --config | String | path/to/project/recources/config.yml | The absolute path to the config File. There are 3 examples preinstalled. Use them by passing `congfig1`, `config2` or `config3` as parameters.|
| -o    | --output | String | -                                    | The absolute path to a folder. All loaded Images will be saved here. |\

The composition of your background image is defined by a config.yml file.\
Read the [Wiki](https://github.com/lennart-rth/Live-Earth-Wallpapers/wiki) for a detailed instruction on how to personalize your Image composition.

***
## For Contributers
1. Read the [Contributing](CONTRIBUTING.md) Readme.
2. Filter Discussions by "For Contributers" Label to find topics to work on.
3. Feel free to add your own ideas, features or open a Discussion in the Discussions tab.

## Known Bugs
### Pypi
1. If `liewa-cli` or `liewa-gui` is not known, add python pip itepackages to system PATH.
### Windows
1. On some Systems the Taskscheduler cant automaticly be set to execute the Programm even when the cimputer is in Battery mode. Therefore you have to manualy unchek this flag in the TaskScheduler for the `liewa` Task.
2. On some Systems the python Packages need to be manualy installed. Do so by typing `pip install bs4 pillow pyyaml requests` into CMD.
