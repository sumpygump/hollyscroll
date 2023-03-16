hollyscroll
===========

Python script that pointlessly scrolls text for you like on computer screens in movies and TV shows

## Installation with pip

```
pip install hollyscroll
```

## Manual Installation

Clone git repository

    $ cd ~/bin
    $ git clone https://github.com/sumpygump/hollyscroll.git hollyscroll-src

Symlink script (assuming `~/bin` is in your `$PATH`)

    $ ln -s hollyscroll-src/hollyscroll.py hollyscroll

## Usage

```
usage: hollyscroll [-h] [-v] [-s {normal,typewriter}] [-l] [-r] [path ...]

Scroll text on terminal window like in movies and TV shows

positional arguments:
  path                  Paths to files or directories to be scrolled

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -s {normal,typewriter}, --style {normal,typewriter}
                        Set output style mode
  -l, --list            Display list of files and mimes only
  -r, --repeat          Repeat listing the files after done

Example:
  hollyscroll ~/Documents

You can also pipe in content from other programs:
  ls -l | hollyscroll
  dmesg | hollyscroll
```
