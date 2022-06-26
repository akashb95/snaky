import json
import logging
import os
from argparse import ArgumentParser
from typing import Any, Collection

from adapters.custom_arg_types import existing_dir_arg_type
from adapters.plz_query import (
    get_build_file_names,
    get_third_party_module_targets,
    get_python_moduledir,
    get_reporoot,
    run_plz_fmt,
)
from domain.build_pkgs.build_pkg import BUILDPkg
from domain.imports.enricher import ToEnrichedImports
from domain.imports.known.known import known_dependencies_from_config
from domain.imports.nodes_collator import NodesCollator
from domain.imports.stdlib_modules import get_stdlib_module_names
from domain.targets.plz.dependency_resolver import DependencyResolver
from domain.targets.plz_target import PlzTarget


def run(build_pkg_dir_paths: list[str], config: dict[str, Any]):
    """

    :param build_pkg_dir_paths: Relative to reporoot
    :param config: Config parsed into dict.
    :return:
    """

    # Get 3rd Party libs and builtins, stdlibs and known imports.
    third_party_modules_targets: set[str] = set(get_third_party_module_targets())
    std_lib_modules: set[str] = get_stdlib_module_names()
    build_file_names: list[str] = get_build_file_names()
    known_dependencies: dict[str, Collection[PlzTarget]] = known_dependencies_from_config(config)

    build_pkgs: list[BUILDPkg] = []
    for build_pkg_dir_path in build_pkg_dir_paths:
        build_pkgs.append(BUILDPkg(build_pkg_dir_path, set(build_file_names)))

    python_moduledir = get_python_moduledir()
    dependency_resolver = DependencyResolver(
        python_moduledir=python_moduledir,
        enricher=ToEnrichedImports(get_reporoot(), python_moduledir),
        std_lib_modules=std_lib_modules,
        available_third_party_module_targets=third_party_modules_targets,
        known_dependencies=known_dependencies,
        nodes_collator=NodesCollator(),
    )

    modified_build_file_paths: list[str] = []
    for build_pkg in build_pkgs:
        build_pkg.resolve_deps_for_targets(dependency_resolver.resolve_deps_for_srcs)
        LOGGER.debug(build_pkg)
        if build_pkg.has_uncommitted_changes():
            build_pkg.write_to_build_file()
            modified_build_file_paths.append(build_pkg.path())

    if modified_build_file_paths:
        run_plz_fmt(*modified_build_file_paths)
        LOGGER.info(f"📢 Modified BUILD files: {', '.join(modified_build_file_paths)}.")
    else:
        LOGGER.info("No BUILD files were modified. Your imports were 👌 already.")
    return


def to_relative_path_from_reporoot(path: str) -> str:
    if not os.path.isabs(path):
        as_abs_path = os.path.abspath(os.path.join(os.getcwd(), path))
    else:
        as_abs_path = path
    without_reporoot_prefix = as_abs_path.removeprefix(get_reporoot())
    if as_abs_path == without_reporoot_prefix:
        raise ValueError(f"{path} not within Plz repo")
    return without_reporoot_prefix.removeprefix(os.path.sep)


def read_config_file(path: str) -> dict[str, Any]:
    if not os.path.isfile(path):
        return {}

    contents: str
    with open(path, "r") as config_file:
        contents = config_file.read()

    try:
        return json.loads(contents)
    except json.JSONDecodeError as e:
        LOGGER.critical("Could not read config file", exc_info=e)
        raise e


if __name__ == "__main__":
    import time
    from common.logger.logger import setup_logger

    parser = ArgumentParser()

    parser.add_argument(
        "build_pkg_dir",
        type=existing_dir_arg_type,
        nargs="+",
        help="BUILD package directories (relative to reporoot)",
    )
    parser.add_argument("--verbose", "-v", action="count", default=0)

    args = parser.parse_args()
    os.environ["PYLLEMI_LOG_LEVEL"] = str(max(0, logging.WARNING - (10 * args.verbose)))

    LOGGER = setup_logger(__file__)

    # Input sanitisation and change dir to reporoot
    build_pkg_dirs = list(map(to_relative_path_from_reporoot, set(args.build_pkg_dir)))
    os.chdir(get_reporoot())

    LOGGER.debug(f"resolving imports for {{{', '.join(build_pkg_dirs)}}}; cwd: {os.getcwd()}")

    config = read_config_file(".pyllemi.json")

    start_time = time.time()
    run(build_pkg_dirs, config)
    duration = time.time() - start_time

    LOGGER.debug(f"Dependency target resolution for {{{', '.join(build_pkg_dirs)}}} took {duration} seconds.")
