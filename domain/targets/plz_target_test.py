from unittest import TestCase

from domain.targets.plz_target import PlzTarget


class TestPlzTarget(TestCase):
    def test_invalid_target_pattern_raises_err(self):
        self.assertRaisesRegex(
            ValueError,
            "potato does not match the format of a canonical BUILD target path",
            PlzTarget,
            "potato",
        )
        return

    def test_with_target_at_reporoot(self):
        plz_target = PlzTarget("//:main")
        self.assertEqual("", plz_target.build_pkg_dir)
        self.assertEqual("main", plz_target.target_name)
        return

    def test_with_absolute_target_path_pattern(self):
        plz_target = PlzTarget("//path/to:target")
        self.assertEqual("path/to", plz_target.build_pkg_dir)
        self.assertEqual("target", plz_target.target_name)
        return

    def test_with_simple_absolute_target_path_pattern(self):
        plz_target = PlzTarget("//path/to")
        self.assertEqual("path/to", plz_target.build_pkg_dir)
        self.assertEqual("to", plz_target.target_name)
        return

    def test_with_relative_target_path_pattern(self):
        plz_target = PlzTarget("//:target")
        self.assertEqual("", plz_target.build_pkg_dir)
        self.assertEqual("target", plz_target.target_name)
        return

    def test_with_tag(self):
        plz_target = PlzTarget("//path/to:target")
        self.assertEqual(
            "//path/to:_target#tag",
            plz_target.with_tag("tag"),
        )
        return

    def test_canonicalize(self):
        plz_target = PlzTarget("//path/to/lib")
        self.assertEqual("//path/to/lib:lib", plz_target.canonicalise())
        return

    def test_simplify_when_absolute_target_path_is_simplest_possible(self):
        plz_target = PlzTarget("//path/to/lib:target")
        self.assertEqual(
            "//path/to/lib:target",
            plz_target.simplify(),
        )
        self.assertEqual("//path/to/lib:target", str(plz_target))
        return

    def test_simplify(self):
        plz_target = PlzTarget("//path/to/lib:lib")
        self.assertEqual(
            "//path/to/lib",
            plz_target.simplify(),
        )
        self.assertEqual("//path/to/lib", str(plz_target))
        return
