import re


class PlzTarget:
    __absolute_target_path_pattern__ = re.compile("^//(.*):([a-zA-Z0-9_]*)$")
    __simple_absolute_target_path_pattern__ = re.compile("^//(.+)$")

    def __init__(self, canonical_build_target_path: str):
        absolute_target_match = re.match(self.__absolute_target_path_pattern__, canonical_build_target_path)
        if absolute_target_match is not None:
            self.build_pkg_dir: str = absolute_target_match.group(1)
            self.target_name: str = (
                absolute_target_match.group(2)
                if absolute_target_match.group(2) != ""
                else self.build_pkg_dir.split("/")[-1]
            )
            return

        simple_absolute_target_match = re.match(
            self.__simple_absolute_target_path_pattern__,
            canonical_build_target_path,
        )
        if simple_absolute_target_match is not None:
            self.build_pkg_dir: str = simple_absolute_target_match.group(1)
            self.target_name: str = self.build_pkg_dir.split("/")[-1]
            return

        else:
            raise ValueError(
                f"{canonical_build_target_path} does not match the format of a canonical BUILD target path"
            )

    def __str__(self):
        return self.simplify()

    def with_tag(self, tag: str) -> str:
        return f"//{self.build_pkg_dir}:_{self.target_name}#{tag}"

    def canonicalise(self) -> str:
        return f"//{self.build_pkg_dir}:{self.target_name}"

    def simplify(self) -> str:
        """
        Simplifies the plz target according to Plz Target conventions.
        I.e. //path/to/lib:lib ≡ //path/to/lib
        """

        build_pkg_dir_split = self.build_pkg_dir.split("/")
        build_pkg_dir_basename: str = ""
        if len(build_pkg_dir_split) > 0:
            build_pkg_dir_basename = build_pkg_dir_split[-1]

        if build_pkg_dir_basename == self.target_name:
            return f"//{self.build_pkg_dir}"

        return f"//{self.build_pkg_dir}:{self.target_name}"