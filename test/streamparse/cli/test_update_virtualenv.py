import argparse
import unittest

from streamparse.cli.update_virtualenv import subparser_hook


def test_subparser_hook():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparser_hook(subparsers)

    subcommands = parser._optionals._actions[1].choices.keys()
    assert "update_virtualenv" in subcommands
