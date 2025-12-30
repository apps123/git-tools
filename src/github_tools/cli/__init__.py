"""CLI command modules for GitHub contribution analytics tools."""

import sys
from typing import Optional

import click

from github_tools import __version__
from github_tools.utils.logging import setup_logging
from github_tools.utils.config import load_config

logger = setup_logging()


@click.group()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress non-error output",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=click.Path),
    default=None,
    help="Configuration file path",
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool, config: Optional[click.Path]) -> None:
    """
    GitHub Developer Contribution Analytics Tools.
    
    A collection of command-line tools for analyzing developer contributions
    across GitHub organization repositories.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set logging level
    if verbose:
        setup_logging(level="DEBUG")
    elif quiet:
        setup_logging(level="ERROR")
    else:
        setup_logging(level="INFO")
    
    # Load configuration
    try:
        ctx.obj["config"] = load_config(config_file=config)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
