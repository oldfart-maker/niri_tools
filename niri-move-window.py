#!/usr/bin/env python3

from util.cli import parse_args
from cmds.move_window import move_window_by_match

def main():
    args = parse_args()
    move_window_by_match(args)

if __name__ == "__main__":
    main()
