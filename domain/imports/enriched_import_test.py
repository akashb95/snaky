import os

from domain.imports.enriched_import import EnrichedImport, ImportType, resolve_import_type, to_whatinputs_input
from utils.mock_python_library_test_case import MockPythonLibraryTestCase


class TestResolveImportType(MockPythonLibraryTestCase):
    def test_import_of_module(self):
        py_import = f"{self.test_dir}.test_module_0"
        self.assertEqual(
            ImportType.MODULE,
            resolve_import_type(py_import, "does.not.matter"),
        )
        return

    def test_builtin_module_import(self):
        self.assertEqual(
            ImportType.UNKNOWN,
            resolve_import_type("os.path", "does.not.matter"),
        )
        return

    def test_import_of_package(self):
        py_import = f"{self.test_dir}.test_subpackage"
        self.assertEqual(
            ImportType.PACKAGE,
            resolve_import_type(py_import, "does.not.matter"),
        )
        return


class TestToWhatInputsInput(MockPythonLibraryTestCase):
    def test_module(self):
        import_ = EnrichedImport("test.module", ImportType.MODULE)
        self.assertEqual(
            [os.path.join("test", "module.py")],
            to_whatinputs_input(import_),
        )
        return

    def test_package(self):
        import_ = EnrichedImport(self.subpackage_dir, ImportType.PACKAGE)
        self.assertEqual(
            [self.subpackage_module],
            to_whatinputs_input(import_),
        )
        return

    def test_unknown_import_type(self):
        import_ = EnrichedImport("test", ImportType.UNKNOWN)
        self.assertIsNone(to_whatinputs_input(import_))
        return

    def test_stub(self):
        import_ = EnrichedImport("test.stub", ImportType.STUB)
        self.assertEqual(
            [os.path.join("test", "stub.pyi")],
            to_whatinputs_input(import_),
        )
        return
