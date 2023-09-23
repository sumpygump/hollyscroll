#!/usr/bin/env python
"""Hollyscroll is a program that scrolls text on a terminal"""

import argparse
import io
import mimetypes
import os
import random
import re
import string
import sys
import time

VERSION = "1.2.2"
PRINTABLE_CHARS = [ord(x) for x in string.printable[:-6]]


class Hollyscroll(object):
    """The text scrolling class"""

    current_file = ""
    """Currently displayed file"""

    filelist = []
    """List of files to render"""

    mode = "print"
    """Mode of operation: print or hex"""

    modes = ["print", "hex"]

    output_style = "normal"
    """Output style"""

    output_styles = ["normal", "typewriter"]

    alter_styles = True
    """Whether styles should automatically alter"""

    pause_time = 1
    """Time in seconds between line prints"""

    repeat = False
    """Whether should be on repeat mode"""

    columns = 120
    """Width of the terminal columns"""

    def __init__(self, filelist, repeat=False, columns=120):
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
        self.columns = columns
        self.generate_pausetime()

    def populate_filelist(self, path):
        """Populate the filelist by recursing a path"""
        for root, dirs, files in os.walk(path):
            # modify "dirs" in place to prevent
            # future code in os.walk from seeing those
            # that start with "."
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            if len(files) == 0:
                continue

            for filename in files:
                if filename.startswith("."):
                    continue
                self.filelist.append(root + "/" + filename)

    def execute(self):
        """Run the scroller"""
        if self.repeat:
            while True:
                self.display_file_data()
        else:
            self.display_file_data()

    def display_file_list(self):
        """Display list of files and mimetypes"""
        for filename in self.filelist:
            filename = os.path.realpath(filename)

            if os.path.isdir(filename):
                continue

            mimetype = mimetypes.guess_type(filename)[0]
            mode = self.determine_mode(filename)

            print("### [" + filename + " " + str(mimetype) + "] ### " + mode)

    def generate_pausetime(self):
        """Set the pause time controlling the scroll speed"""
        self.pause_time = random.random()

    def next_mode(self):
        try:
            mode_index = self.modes.index(self.mode)
            mode_index = mode_index + 1
        except ValueError:
            mode_index = 0

        if mode_index >= len(self.modes):
            mode_index = 0

        self.mode = self.modes[mode_index]

    def select_random_output_style(self):
        if not self.alter_styles:
            return False

        self.output_style = random.choice(self.output_styles)

    def display_stream(self, stream):
        reading_as_text = True
        offset = 0
        size = self.determine_xxd_size()
        while True:
            try:
                if reading_as_text:
                    # Read two bytes first to see if we need to switch to binary mode
                    line = stream.readline(2)
                    line = "{}{}".format(line, stream.readline())
                    if line in ("", b""):
                        break

                    self.printline(line.rstrip())
                    time.sleep(self.pause_time)
                else:
                    offset = self.display_binary_stream(stream, size, offset)
                    if offset is None:
                        break
            except UnicodeDecodeError:
                reading_as_text = False
                offset = self.display_binary_stream(stream, size, offset)
                if offset is None:
                    break
                continue
            except KeyboardInterrupt:
                print("---")
                break

        print()

    def display_binary_stream(self, stream, size=16, offset=0):
        buf = stream.buffer.read(size)
        if not buf:
            return None
        line = self.xxd_line(buf, line_offset=offset, size=size)
        self.printline(line)
        time.sleep(self.pause_time)
        return offset + 1

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

            print("### [" + filename + " " + str(mimetype) + "] ### " + self.mode)

            try:
                if self.mode == "print":
                    with io.open(filename, "r", encoding="utf-8") as stream:
                        for line in stream:
                            self.printline(line)
                            time.sleep(self.pause_time)
                else:
                    size = self.determine_xxd_size()
                    with io.open(filename, "rb") as stream:
                        offset = 0
                        while True:
                            buf = stream.read(size)
                            if not buf:
                                break
                            line = self.xxd_line(buf, line_offset=offset, size=size)
                            self.printline(line)
                            time.sleep(self.pause_time)
                            offset += 1
            # pylint: disable=broad-exception-caught
            except Exception:  # Handle ANY exception here.
                continue

            print()

    def determine_mode(self, filename):
        hollytypes = HollyTypes()

        mimetype = mimetypes.guess_type(filename)[0]

        # print_types or print_extensions will force the mode to print
        if hollytypes.is_print_type(mimetype, filename):
            return "print"

        # Fallback to hex mode
        return "hex"

    def determine_xxd_size(self):
        # This calculation will ensure the right number of bytes to focus on in
        # the xxd translation accounting for the terminal size
        size = int(self.columns / 4.3)
        return size if size % 2 == 0 else size - 1

    def printline(self, line):
        if self.output_style == "typewriter":
            if line[-1] != "\n":
                line = "{}\n".format(line)
            self.typeline(line)
        else:
            print(line.rstrip())

    def typeline(self, line):
        # If the line starts with white space, don't echo out each space one at
        # a time, but in one big chunk (it looks better)
        startchar = len(re.match(r"\s*", line, re.UNICODE).group(0))
        if startchar > 0:
            sys.stdout.write("%s" % line[0:startchar])
            sys.stdout.flush()
            time.sleep(0.1)
            line = line[startchar:]

        for character in line:
            sys.stdout.write("%s" % character)
            sys.stdout.flush()
            time.sleep(0.1)

    def xxd_line(self, buf, line_offset=0, size=16):
        """Make an xxd line from some bytes"""

        buf_hex = buf.hex()
        octets_group_count = 4
        panel_b_width = round(size * 2 + ((size * 2 / octets_group_count) - 1))

        template = "{0}: {1:<MAX}  {2}".replace("MAX", str(panel_b_width))
        return template.format(
            "{:07x}".format(line_offset * size),
            " ".join(
                [
                    "".join(buf_hex[i : i + octets_group_count])
                    for i in range(0, len(buf_hex), octets_group_count)
                ]
            ),
            "".join([chr(c) if c in PRINTABLE_CHARS else "." for c in buf]),
        )


class HollyTypes(object):
    """Class for handling different file type scenarios"""

    print_types = [
        "application/javascript",
        "application/json",
        "application/x-httpd-php",
        "application/x-sh",
        "application/xml",
    ]

    print_extensions = [
        ".1",
        ".asm",
        ".aux",
        ".awk",
        ".bat",
        ".cfg",
        ".conf",
        ".ini",
        ".json",
        ".log",
        ".lua",
        ".md",
        ".md",
        ".php",
        ".phtml",
        ".rst",
        ".sbt",
        ".sql",
        ".svg",
        ".toml",
        ".twig",
        ".yaml",
        ".yml",
    ]

    # List of filenames without extensions that should be print mode
    print_filenames = ["makefile", "readme", "changelog", "license"]

    def read_first_line(self, filename):
        """Read the first line of a file"""
        with open(filename, encoding="utf-8") as file_data:
            return file_data.readline()
        return ""

    def is_print_type(self, mimetype, filename):
        # Get the file extension
        # (splitext returns filename,extension)
        (filename, extension) = os.path.splitext(filename)

        if os.path.split(filename)[1].lower() in self.print_filenames:
            return True

        if (
            mimetype is not None
            and mimetype in self.print_types
            or extension in self.print_extensions
        ):
            return True

        if mimetype is not None and mimetype[:4] == "text":
            return True

        try:
            # last ditch effort to determine if file should be print mode
            first_line = self.read_first_line(filename)
            if first_line[:2] == "#!":
                # shebang found, switch to print mode
                return True
        except:  # Don't fail from anything pylint: disable=bare-except
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
        epilog="""\
Example:
  hollyscroll ~/Documents

You can also pipe in content from other programs:
  ls -l | hollyscroll""",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + VERSION
    )
    parser.add_argument(
        "-s", "--style", choices=Hollyscroll.output_styles, help="Set output style mode"
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="Display list of files and mimes only"
    )
    parser.add_argument(
        "-r",
        "--repeat",
        action="store_true",
        help="Repeat listing the files after done",
    )

    # By default hollyscroll will use the current directory (.)
    parser.add_argument(
        "paths",
        metavar="path",
        nargs="*",
        default=".",
        help="Paths to files or directories to be scrolled",
    )

    # This will read sys.argv and process the above parser rules
    args = parser.parse_args()
    columns = os.get_terminal_size().columns

    if sys.stdin.isatty():
        # Check arguments. User can specify a list of arguments as files or
        # directories to read and scroll.
        path = select_path(args.paths)
        hollyscroll = Hollyscroll(path, repeat=args.repeat, columns=columns)

        if args.style:
            hollyscroll.output_style = args.style
            hollyscroll.alter_styles = False

        try:
            if args.list:
                hollyscroll.display_file_list()
            else:
                hollyscroll.execute()
        except KeyboardInterrupt:
            print("---")
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
