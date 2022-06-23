import os
import logging
from argparse import ArgumentParser

from adapters.custom_arg_types import existing_dir_arg_type
from adapters.plz_query import (
    get_build_file_names,
    get_third_party_module_targets,
    get_python_moduledir,
    get_reporoot,
)
from domain.build_pkgs.build_pkg import BUILDPkg
from domain.imports.enricher import ToEnrichedImports
from domain.imports.nodes_collator import NodesCollator
from domain.imports.stdlib_modules import get_stdlib_module_names
from domain.targets.plz.dependency_resolver import DependencyResolver


def run(build_pkg_dir_paths: list[str]):
    """

    :param build_pkg_dir_paths: Relative to reporoot
    :return:
    """

    # Get 3rd Party libs and builtins
    third_party_modules_targets: set[str] = set(get_third_party_module_targets())
    std_lib_modules: set[str] = get_stdlib_module_names()
    build_file_names: list[str] = get_build_file_names()

    build_pkg_dirs: list[BUILDPkg] = []
    for build_pkg_dir_path in build_pkg_dir_paths:
        build_pkg_dirs.append(BUILDPkg(build_pkg_dir_path, set(build_file_names)))

    python_moduledir = get_python_moduledir()
    dependency_resolver = DependencyResolver(
        python_moduledir=python_moduledir,
        enricher=ToEnrichedImports(get_reporoot(), python_moduledir),
        std_lib_modules=std_lib_modules,
        available_third_party_module_targets=third_party_modules_targets,
        nodes_collator=NodesCollator(),
    )

    for build_pkg_dir in build_pkg_dirs:
        build_pkg_dir.resolve_deps_for_targets(dependency_resolver.resolve_deps_for_srcs)
        print(build_pkg_dir)
        # TODO: trial by fire... RUN THE DAMN THING
    return


if __name__ == "__main__":
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
    print(log_level := max(0, logging.WARNING - (10 * args.verbose)))
    os.environ["PYLLEMI_LOG_LEVEL"] = str(log_level)

    LOGGER = setup_logger(__file__)

    build_pkg_dirs_arg = args.build_pkg_dir
    LOGGER.info(f"resolving imports for {', '.join(build_pkg_dirs_arg)}; cwd: {os.getcwd()}")
    run(build_pkg_dirs_arg)
