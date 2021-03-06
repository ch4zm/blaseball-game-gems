import sys
import os
import json
import argparse
from .view import JsonView, TextView, MarkdownView
from .util import CaptureStdout


def main(sysargs = sys.argv[1:]):

    p = argparse.ArgumentParser()

    p.add_argument('-v',
                   '--version',
                   required=False,
                   default=False,
                   action='store_true',
                   help='Print program name and version number and exit')

    p.add_argument('-i',
                   '--input-file',
                   required=True,
                   help='Input JSON file (output from game-summary)')

    g = p.add_mutually_exclusive_group()
    g.add_argument('--text',
                   action='store_true',
                   default=False,
                   help='Output in plain text format')
    g.add_argument('--markdown',
                   action='store_true',
                   default=False,
                   help='Output in markdown format')
    g.add_argument('--json',
                   action='store_true',
                   default=False,
                   help='Output in JSON format')

    # Print help, if no arguments provided
    if len(sysargs)==0:
        p.print_help()
        exit(0)

    # Parse arguments
    options = p.parse_args(sysargs)

    # If the user asked for the version,
    # print the version number and exit.
    if options.version:
        from . import _program, __version__
        print(_program, __version__)
        sys.exit(0)

    if (not options.markdown) and (not options.text) and (not options.json):
        options.json = True

    if options.text:
        v = TextView(options)
        v.show()
    elif options.markdown:
        v = MarkdownView(options)
        v.show()
    elif options.json:
        v = JsonView(options)
        v.show()


# To call the Python API, pass a game summary
# in JSON string format
def game_gems(sysargs, json_game_summary):
    import tempfile
    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as f:
            f.write(json_game_summary)
        with CaptureStdout() as so:
            main(sysargs+["-i", f.name])
    return str(so)


if __name__ == '__main__':
    main()
