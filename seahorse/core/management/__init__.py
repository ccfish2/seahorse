import functools
import  pkgutil
import sys
import os
from importlib import import_module
from seahorse.utils.version import get_version

from seahorse.core.management.base import(
     CommandParser,
     CommandError, 
     BaseCommand,
     handle_default_options)

def find_commands(management_dir):
    """
    Given a path to a management directory, 
    return a list of all the command
    names that are available
    """
    command_dir = os.path.join(management_dir, "commands")
    return [
        name 
        for _, name, is_pkg in pkgutil.iter_modules([command_dir])
        if not is_pkg and not name.startswith("_")
    ]

def load_command_class(app_name, name):
    """
    Given a command name and application name, 
    return the Command class instance
    """
    module = import_module("%s.management.commands.%s" % (app_name, name))
    return module.Command()

@functools.cache
def get_commands():
    """
    Return a dictionary mapping command names to their callback
    application
    the dictionary is cached on the first call and reused on 
    subsequent calls
    """
    commands = {name:"seahorse.core" for name in find_commands(__path__[0])}
    return commands

class ManagementUtility:

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        if self.prog_name == "__main__.py":
            self.prog_name = "python3 -m seahorse"
        self.settings_exception = None

    def main_help_text(self, subcommand):
        pass

    def fetch_command(self, subcommand):
        """
        Try to fetch the given subcommand
        """
        commands = get_commands()
        try:
            app_name = commands[subcommand]
        except KeyError:
            sys.stderr.write("Unknown command: %r" % subcommand)
            sys.exit(1)

        if isinstance(app_name, BaseCommand):
            klass = app_name
        else:
            klass = load_command_class(app_name, subcommand)
        return klass
    
    def execute(self):
        """
        given arguments, figure out which subcommand should 
        run, create a parser appropriate to that command and run 
        it
        """
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = "help"
        
        parser = CommandParser()
        parser.add_argument("args", nargs="*")

        try:
            options, args = parser.parse_known_args(self.argv[2:])
            handle_default_options(options)
        except CommandError:
            pass


        if subcommand == "help":
            if "--commands" in args:
                sys.stdout.write(self.main_help_text(commands_only=True)+"\n")
            elif not options.args:
                sys.stdout.write(self.main_help_text() + "\n")
            else:
                self.fetch_command(options.args[0].print_help(self.prog_name,
                options.args[0]))
        if subcommand == "version" or self.argv[1:] == ["--version"]:
            sys.stdout.write(get_version() + "\n")
        if self.argv[1:] in (["--help"], ["-h"]):
            sys.stdout.write(self.main_help_text() + "\n")
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)

def execute_from_command_line(argv=None):
    """ Run the command line """
    utility = ManagementUtility(argv)
    utility.execute()