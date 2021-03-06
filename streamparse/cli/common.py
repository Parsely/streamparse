"""
Functions for adding common CLI arguments to argparse sub-commands.
"""
import argparse
import copy
import warnings

from ruamel import yaml

from streamparse.util import get_storm_workers


class _StoreDictAction(argparse.Action):
    """Action for storing key=val option strings as a single dict."""

    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):
        if nargs == 0:
            raise ValueError("nargs for store_dict actions must be > 0")
        if const is not None and nargs != "?":
            raise ValueError('nargs must be "?" to supply const')
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, {})
        # Only doing a copy here because that's what _AppendAction does
        items = copy.copy(getattr(namespace, self.dest))
        key, val = values.split("=", 1)
        if yaml.version_info < (0, 15):
            items[key] = yaml.safe_load(val)
        else:
            yml = yaml.YAML(typ="safe", pure=True)
            items[key] = yml.load(val)
        setattr(namespace, self.dest, items)


def option_alias(option):
    """Returns a function that will create option=val for _StoreDictAction."""

    def _create_key_val_str(val):
        return f"{option}={val}"

    return _create_key_val_str


def add_ackers(parser):
    """ Add --ackers option to parser """
    parser.add_argument(
        "-a",
        "--ackers",
        help="Set number of acker executors for your topology. "
        "Defaults to the number of worker nodes in your "
        "Storm environment.",
        type=option_alias("topology.acker.executors"),
        action=_StoreDictAction,
        dest="options",
    )


def add_config(parser):
    """ Add --config option to parser """
    parser.add_argument(
        "--config", help="Specify path to config.json", type=argparse.FileType("r")
    )


def add_debug(parser):
    """ Add --debug option to parser """
    parser.add_argument(
        "-d",
        "--debug",
        help="Set topology.debug and produce debugging output.",
        type=option_alias("topology.debug"),
        action=_StoreDictAction,
        dest="options",
        const="true",
        nargs="?",
    )


def add_environment(parser):
    """ Add --environment option to parser """
    parser.add_argument(
        "-e",
        "--environment",
        help="The environment to use for the command.  "
        "Corresponds to an environment in your "
        '"envs" dictionary in config.json.  If you '
        "only have one environment specified, "
        "streamparse will automatically use this.",
    )


def add_name(parser):
    """ Add --name option to parser """
    parser.add_argument(
        "-n",
        "--name",
        help="The name of the topology to act on.  If you have "
        'only one topology defined in your "topologies" '
        "directory, streamparse will use it "
        "automatically.",
    )


def add_options(parser):
    """ Add --option options to parser """
    parser.add_argument(
        "-o",
        "--option",
        dest="options",
        action=_StoreDictAction,
        help="Topology option to pass on to Storm. For example,"
        ' "-o topology.debug=true" is equivalent to '
        '"--debug".  May be repeated multiple for multiple'
        " options.",
    )


def add_override_name(parser):
    """ Add --override_name option to parser """
    parser.add_argument(
        "-N",
        "--override_name",
        help="For operations such as creating virtualenvs and "
        "killing/submitting topologies, use this value "
        "instead of NAME.  This is useful if you want to "
        "submit the same topology twice without having to "
        "duplicate the topology file.",
    )


def add_overwrite_virtualenv(parser):
    """ Add --overwrite_virtualenv option to parser """
    parser.add_argument(
        "--overwrite_virtualenv",
        help="Create the virtualenv even if it already exists."
        " This is useful when you have changed your "
        "virtualenv_flags.",
        action="store_true",
    )


def add_pattern(parser):
    """ Add --pattern option to parser """
    parser.add_argument("--pattern", help="Pattern of log files to operate on.")


def add_pool_size(parser):
    """ Add --pool_size option to parser """
    parser.add_argument(
        "--pool_size",
        help="Number of simultaneous SSH connections to use when updating "
        "virtualenvs, removing logs, or tailing logs.",
        default=10,
        type=int,
    )


def add_requirements(parser):
    """ Add --requirements option to parser """
    parser.add_argument(
        "-r",
        "--requirements",
        nargs="*",
        help="Path to pip-style requirements file specifying "
        "the dependencies to use for creating the "
        "virtualenv for this topology.  If unspecified, "
        "streamparse will look for a file called NAME.txt "
        "in the directory specified by the "
        "virtualenv_specs setting in config.json.",
    )


def add_simple_jar(parser):
    """ Add --simple_jar option to parser. """
    parser.add_argument(
        "-s",
        "--simple_jar",
        action="store_true",
        help="Instead of creating an Uber-JAR for the "
        "topology, which contains all of its JVM "
        "dependencies, create a simple JAR with just the "
        "code for the project.  This is useful when your "
        "project is pure Python and has no JVM "
        "dependencies.",
    )


def add_timeout(parser):
    """ Add --timeout option to parser """
    parser.add_argument(
        "--timeout",
        type=int,
        default=7000,
        help="Milliseconds to wait for Nimbus to respond. " "(default: %(default)s)",
    )


def add_user(parser, allow_short=False):
    """Add --user option to parser

    Set allow_short to add -u as well.
    """
    args = ["--user"]
    if allow_short:
        args.insert(0, "-u")

    kwargs = {
        "help": "User argument to sudo when creating and deleting virtualenvs.",
        "default": None,
        "type": option_alias("sudo_user"),
        "dest": "options",
        "action": _StoreDictAction,
    }

    parser.add_argument(*args, **kwargs)


def add_wait(parser):
    """ Add --wait option to parser """
    parser.add_argument(
        "--wait",
        type=int,
        default=5,
        help="Seconds to wait before killing topology. " "(default: %(default)s)",
    )


def add_workers(parser):
    """ Add --workers option to parser """
    parser.add_argument(
        "-w",
        "--workers",
        help="Set number of Storm workers for your topology. "
        "Defaults to the number of worker nodes in your "
        "Storm environment.",
        type=option_alias("topology.workers"),
        action=_StoreDictAction,
        dest="options",
    )


VIRTUALENV_OPTIONS = (
    "install_virtualenv",
    "use_virtualenv",
    "virtualenv_flags",
    "virtualenv_root",
    "virtualenv_name",
)


def resolve_options(
    cli_options, env_config, topology_class, topology_name, local_only=False
):
    """Resolve potentially conflicting Storm options from three sources:

    CLI options > Topology options > config.json options

    :param local_only: Whether or not we should talk to Nimbus to get Storm
                       workers and other info.
    """
    storm_options = {}

    # Start with environment options
    storm_options.update(env_config.get("options", {}))

    # Set topology.python.path
    if env_config.get("use_virtualenv", True):
        python_path = "/".join(
            [env_config["virtualenv_root"], topology_name, "bin", "python"]
        )
        # This setting is for information purposes only, and is not actually
        # read by any pystorm or streamparse code.
        storm_options["topology.python.path"] = python_path

    # Set logging options based on environment config
    log_config = env_config.get("log", {})
    log_path = log_config.get("path") or env_config.get("log_path")
    log_file = log_config.get("file") or env_config.get("log_file")
    if log_path:
        storm_options["pystorm.log.path"] = log_path
    if log_file:
        storm_options["pystorm.log.file"] = log_file
    if isinstance(log_config.get("max_bytes"), int):
        storm_options["pystorm.log.max_bytes"] = log_config["max_bytes"]
    if isinstance(log_config.get("backup_count"), int):
        storm_options["pystorm.log.backup_count"] = log_config["backup_count"]
    if isinstance(log_config.get("level"), str):
        storm_options["pystorm.log.level"] = log_config["level"].lower()

    # Make sure virtualenv options are present here
    for venv_option in VIRTUALENV_OPTIONS:
        if venv_option in env_config:
            storm_options[venv_option] = env_config[venv_option]

    # Set sudo_user default to SSH user if we have one
    storm_options["sudo_user"] = env_config.get("user", None)

    # Override options with topology options
    storm_options.update(topology_class.config)

    # Override options with CLI options
    storm_options.update(cli_options or {})

    # Set log level to debug if topology.debug is set
    if storm_options.get("topology.debug", False):
        storm_options["pystorm.log.level"] = "debug"

    # If ackers and executors still aren't set, use number of worker nodes
    if not local_only:
        if not storm_options.get("storm.workers.list"):
            storm_options["storm.workers.list"] = get_storm_workers(env_config)
        elif isinstance(storm_options["storm.workers.list"], str):
            storm_options["storm.workers.list"] = storm_options[
                "storm.workers.list"
            ].split(",")
        num_storm_workers = len(storm_options["storm.workers.list"])
    else:
        storm_options["storm.workers.list"] = []
        num_storm_workers = 1
    if storm_options.get("topology.acker.executors") is None:
        storm_options["topology.acker.executors"] = num_storm_workers
    if storm_options.get("topology.workers") is None:
        storm_options["topology.workers"] = num_storm_workers

    # If sudo_user was not present anywhere, set it to "root"
    storm_options.setdefault("sudo_user", "root")

    return storm_options


def warn_about_deprecated_user(user, func_name):
    if user is not None:
        warnings.warn(
            (
                "The 'user' argument to '{}' will be removed in the next "
                "major release of streamparse. Provide the 'sudo_user' key to"
                " the 'options' dict argument instead."
            ).format(func_name),
            DeprecationWarning,
        )
