#!/usr/bin/env python
"""Hollyscroll is a program that scrolls text on a terminal"""

import os
import time
import random
import sys
import mimetypes
import re
import argparse

VERSION="1.2.1"

class Hollyscroll(object):
    """The text scrolling class"""

    current_file = ''
    """Currently displayed file"""

    filelist = []
    """List of files to render"""

    mode = 'print'
    """Mode of operation: print or hex"""

    modes = ['print', 'hex']

    output_style = 'normal'
    """Output style"""

    output_styles = ['normal', 'typewriter']

    alter_styles = True
    """Whether styles should automatically alter"""

    pause_time = 1
    """Time in seconds between line prints"""

    repeat = False
    """Whether should be on repeat mode"""

    def __init__(self, filelist, repeat=False):
        """Constructor"""
        self.filelist = []

        if filelist:
            print("Reading file list")
            for filename in filelist:
                if os.path.isdir(filename):
                    self.populate_filelist(filename)
                else:
                    self.filelist.append(filename)

            print("{0} files to display".format(len(self.filelist)))

        self.repeat = repeat
        self.generate_pausetime()

    def populate_filelist(self, path):
        """Populate the filelist by recursing a path"""
        for root,dirs,files in os.walk(path):
            # modify "dirs" in place to prevent
            # future code in os.walk from seeing those
            # that start with "."
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            if len(files) == 0:
                continue

            for filename in files:
                if filename.startswith('.'):
                    continue
                self.filelist.append(root + '/' + filename)

    def execute(self):
        """Run the scroller"""
        if self.repeat:
            while True:
                self.display_file_data()
        else:
            self.display_file_data()

    def display_file_list(self):
        """Display list of files and mimetypes"""
        hollytypes = HollyTypes()

        for filename in self.filelist:
            filename = os.path.realpath(filename)

            if os.path.isdir(filename):
                continue

            mimetype = mimetypes.guess_type(filename)[0]
            mode = self.determine_mode(filename)

            print('### [' + filename + ' ' + str(mimetype) + '] ### ' + mode)

    def generate_pausetime(self):
        """Set the pause time controlling the scroll speed"""
        self.pause_time = random.random()

    def next_mode(self):
        try:
            mode_index = self.modes.index(self.mode)
            mode_index = mode_index + 1
        except ValueError as error:
            mode_index = 0

        if mode_index >= len(self.modes):
            mode_index = 0

        self.mode = self.modes[mode_index]

    def select_random_output_style(self):
        if not self.alter_styles:
            return False

        self.output_style = random.choice(self.output_styles)

    def display_stream(self, stream):
        while 1:
            try:
                line = stream.readline()
                if line == '':
                    break
                self.printline(line)
                time.sleep(self.pause_time)
            except KeyboardInterrupt as error:
                print('---')
                break

        print()

    def display_file_data(self):
        for filename in self.filelist:
            self.generate_pausetime()
            filename = os.path.realpath(filename)
            self.current_file = filename
            self.next_mode()
            self.select_random_output_style()

            if os.path.isdir(filename):
                continue

            mimetype = mimetypes.guess_type(filename)[0]
            self.mode = self.determine_mode(filename)

            try:
                if self.mode == 'print':
                    lines = self.read_file_data_print(filename)
                else:
                    lines = self.read_file_data_hex(filename)
            except:
                continue

            print('### [' + filename + ' ' + str(mimetype) + '] ### ' + self.mode)
            for line in lines:
                self.printline(line)
                time.sleep(self.pause_time)
            print()

    def determine_mode(self, filename):
        hollytypes = HollyTypes()

        mimetype = mimetypes.guess_type(filename)[0]

        # print_types or print_extensions will force the mode to print
        if hollytypes.is_print_type(mimetype, filename):
            return 'print'

        # Fallback to hex mode
        return 'hex'

    def printline(self, line):
        if self.output_style == 'typewriter':
            self.typeline(line),
        else:
            print(line.strip()),

    def typeline(self, line):
        # If the line starts with white space, don't echo out each space one at
        # a time, but in one big chunk (it looks better)
        startchar = len(re.match(r"\s*", line, re.UNICODE).group(0))
        if startchar > 0:
            sys.stdout.write('%s' % line[0:startchar])
            sys.stdout.flush()
            time.sleep(0.1)
            line = line[startchar:]

        for character in line:
            sys.stdout.write('%s' % character)
            sys.stdout.flush()
            time.sleep(0.1)

    def read_file_data_print(self, filename):
        """Read in a file for print mode"""
        file_data = open(filename)
        return file_data.readlines()

    def read_file_data_hex(self, filename):
        """Read in a file for hex mode"""
        cmd = "xxd '" + filename + "' > /tmp/holly"
        os.system(cmd)
        file_data = open('/tmp/holly')
        return file_data.readlines()

class HollyTypes(object):
    print_types = [
        'application/javascript',
        'application/json',
        'application/x-httpd-php',
        'application/x-sh',
        'application/xml',
    ]

    print_extensions = [
        '.aux',
        '.awk',
        '.bat',
        '.conf',
        '.json',
        '.ini',
        '.log',
        '.lua',
        '.md',
        '.php',
        '.phtml',
        '.sql',
        '.twig',
        '.yml',
        '.sbt',
        '.md',
        '.asm',
        '.svg',
        '.1',
        '.cfg',
        '.rst',
    ]

    # List of filenames without extensions that should be print mode
    print_filenames = [
        'makefile',
        'readme',
        'changelog',
        'license'
    ]

    def read_first_line(self, filename):
        """Read the first line of a file"""
        file_data = open(filename)
        return file_data.readline()

    def is_print_type(self, mimetype, filename):
        # Get the file extension
        # (splitext returns filename,extension)
        (filename, extension) = os.path.splitext(filename)

        if os.path.split(filename)[1].lower() in self.print_filenames:
            return True

        if mimetype != None and mimetype in self.print_types \
            or extension in self.print_extensions:
                return True

        if mimetype != None and mimetype[:4] == 'text':
            return True

        try:
            # last ditch effort to determine if file should be print mode
            first_line = self.read_first_line(filename)
            if (first_line[:2] == '#!'):
                # shebang found, switch to print mode
                return True
        except:
            return False

        return False

def select_path(paths):
    """Select realpaths from list of strings"""
    realpaths = []
    for item in paths:
        if not os.path.exists(item):
            sys.stderr.write("Warning: path '{0}' not found.\n".format(item))
            continue
        realpaths.append(os.path.realpath(item))

    return realpaths

def main():
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Scroll text on terminal window like in movies and TV shows",
        epilog='''\
Example:
  hollyscroll ~/Documents

You can also pipe in content from other programs:
  ls -l | hollyscroll'''
    )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
    parser.add_argument('-s', '--style', choices=Hollyscroll.output_styles, help="Set output style mode")
    parser.add_argument('-l', '--list', action='store_true', help="Display list of files and mimes only")
    parser.add_argument('-r', '--repeat', action='store_true', help="Repeat listing the files after done")

    # By default hollyscroll will use the current directory (.)
    parser.add_argument('paths', metavar='path', nargs='*', default='.', help="Paths to files or directories to be scrolled")

    # This will read sys.argv and process the above parser rules
    args = parser.parse_args()

    if sys.stdin.isatty():
        # Check arguments. User can specify a list of arguments as files or
        # directories to read and scroll.
        path = select_path(args.paths)
        hollyscroll = Hollyscroll(path, repeat=args.repeat)

        if args.style:
            hollyscroll.output_style = args.style
            hollyscroll.alter_styles = False

        try:
            if args.list:
                hollyscroll.display_file_list()
            else:
                hollyscroll.execute()
        except KeyboardInterrupt as error:
            print('---')
    else:
        # Stdin mode, content is piped in from another program
        # e.g. ls -l | hollyscroll -s normal
        hollyscroll = Hollyscroll([])

        if args.style:
            hollyscroll.output_style = args.style

        hollyscroll.display_stream(sys.stdin)

    sys.exit(0)

if __name__ == "__main__":
    main()
