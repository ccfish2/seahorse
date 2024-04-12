
from argparse import ArgumentParser, HelpFormatter
import argparse
from functools import partial
from io import TextIOBase
import os
from seahorse.core.exception import ImproperlyConfigured
from seahorse.utils.version import get_version

from seahorse.db import DEFAULT_DB_ALIAS, connections
import sys

ALL_CHECKS = "__all__"
class OutputWrapper(TextIOBase):
    """
    Wrapper around stdout/stderr
    """

    @property
    def style_func(self):
        return self._style_func

    @style_func.setter
    def style_func(self, style_func):
        if style_func and self.isatty():
            self._style_func = style_func
        else:
            self._style_func = lambda x: x

    def __init__(self, out, ending="\n"):
        self._out = out
        self.style_func = None
        self.ending = ending

    def __getattr__(self, name):
        return getattr(self._out, name)

    def flush(self):
        if hasattr(self._out, "flush"):
            self._out.flush()

    def isatty(self):
        return hasattr(self._out, "isatty") and self._out.isatty()

    def write(self, msg="", style_func=None, ending=None):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(style_func(msg))

class CommandError(Exception):
    """
    Exception class indicating a problem while executing a command
    """
    def __init__(self, *args, returncode=1, **kwargs):
        self.returncode = returncode
        super().__init__(*args, **kwargs)

class SystemCheckError(CommandError):
    pass

class CommandParser(ArgumentParser):
    def __init__(
        self, *, missing_args_message=None, called_from_command_line=None, **kwargs
    ):
        self.missing_args_message = missing_args_message
        self.called_from_command_line = called_from_command_line
        super().__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if self.missing_args_message and not (
            args or any(not arg.startswith("-") for arg in args)
        ):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        if self.called_from_command_line:
            super().error(message)
        else:
            raise CommandError("Error: %s" % message)

    def add_subparsers(self, **kwargs):
        parser_class = kwargs.get("parser_class", type(self))
        if issubclass(parser_class, CommandParser):
            kwargs["parser_class"] = partial(
                parser_class,
                called_from_command_line=self.called_from_command_line,
            )
        return super().add_subparsers(**kwargs)

class SeahorseHelpFormatter(HelpFormatter):
    """
    Customized formatter so that command-specific arguments appear in the
    --help output before arguments common to all commands.
    """

    show_last = {
        "--version",
        "--verbosity",
        "--traceback",
        "--settings",
        "--pythonpath",
        "--no-color",
        "--force-color",
        "--skip-checks",
    }

    def _reordered_actions(self, actions):
        return sorted(
            actions, key=lambda a: set(a.option_strings) & self.show_last != set()
        )

    def add_usage(self, usage, actions, *args, **kwargs):
        super().add_usage(usage, self._reordered_actions(actions), *args, **kwargs)

    def add_arguments(self, actions):
        super().add_arguments(self._reordered_actions(actions))

class BaseCommand:
    """
    The base class from which all management commands ultimately 
    derive
    """

    help = ""
    requires_system_checks = "__all__"
    base_stealth_options = ("stderr", "stdout")
    stealth_options=()
    suppressed_base_arguments = set()

    def __init__(self, stdout=None, stderr=None):
        self.stdout=OutputWrapper(stdout or sys.stdout)
        self.stderr=OutputWrapper(stderr or sys.stderr)
        if (
            not isinstance(self.requires_system_checks, (list, tuple))
            and self.requires_system_checks != ALL_CHECKS
        ):
            raise TypeError("requires_system_checks must be a list or tuple.")
    
    def get_version(self):
        return get_version()
    
    def create_parser(self, prog_name, subcommand, **kwargs):
        kwargs.setdefault("formatter_class", SeahorseHelpFormatter)
        parser = CommandParser(
            prog="%s %s" %(os.path.basename(prog_name), subcommand),
            description=self.help or None,
            missing_args_message=getattr(self, "missing_args_message",None),
            called_from_command_line=getattr(self, "called_from_command_line", None),
            **kwargs,
        )
        self.add_base_argument(
            parser,
            "--version",
            action="version",
            version=self.get_version(),
            help="Show program's version number and exit.",
        )
        self.add_base_argument(
            parser,
            "-v",
            "--verbosity",
            default=1,
            type=int,
            choices=[0,1,2,3],
        )
        self.add_arguments(parser)
        return parser
    
    def add_arguments(self, parser):
        pass
    
    def add_base_argument(self, parser, *args, **kwargs):
        for arg in args:
            if arg in self.suppressed_base_arguments:
                kwargs["help"] = argparse.SUPPRESS
                break
        parser.add_argument(*args, **kwargs)

    def print_help(self, prog_name, subcommand):
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # remove positional args out of options
        args = cmd_options.pop("args", ())
        handle_default_options(options) 
        try:
            self.execute(*args, **cmd_options)
        except CommandError as e:
            if options.traceback:
                raise
        finally:
            try:
                connections.close_all()
            except ImproperlyConfigured:
                pass

    def execute(self, *args, **options):
        """
        Execute the command
        Todo:
            Add preparation checklist if there is a need
        """
        if options.get("stdout"):
            self.stdout = OutputWrapper(options["stdout"])
        if options.get("stderr"):
            self.stderr = OutputWrapper(options["stderr"])
       
        if self.requires_system_checks and "skip_checks" not in options:
            if self.requires_system_checks == ALL_CHECKS:
                print("do the check")
            else:
                print("checking specific stuff")
        output = self.handle(*args, **options)
        if output:
            if self.output_transaction:
                connection = connections[options.get("database", DEFAULT_DB_ALIAS)]
                output = "%s\n%s\n%s" %()
            self.stdout.write(output)
        return output
            
def handle_default_options(options):
    """
    include default options that all comamnds should accept
    so that the mgmtutility could handle them before 
    sending to commands
    """
    pass 

        


