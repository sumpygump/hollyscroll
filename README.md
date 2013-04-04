hollyscroll
===========

Python script that pointlessly scrolls text for you like on computer screens in movies and TV shows

## Installation

Clone git repository

    $ cd ~/bin
    $ git clone git://github.com/sumpygump/hollyscroll.git hollyscroll-src

Symlink script

    $ ln -s hollyscroll-src/hollyscroll

## Usage

```
usage: hollyscroll [-h] [-v] [-s {normal,typewriter}] [path [path ...]]

positional arguments:
  path                  Paths to files or directories to be scrolled

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -s {normal,typewriter}, --style {normal,typewriter}
                        Set output style mode
```

You can also pipe in content from other programs

    ls -l | hollyscroll

    tail -f /var/log/apache2/error.log | hollyscroll
