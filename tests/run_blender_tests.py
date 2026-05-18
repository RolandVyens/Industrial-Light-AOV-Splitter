import importlib.util
import os
import pathlib
import sys
import unittest


def load_addon():
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    init_py = repo_root / "__init__.py"
    module_name = "industrial_light_aov_splitter_tests"
    spec = importlib.util.spec_from_file_location(
        module_name,
        init_py,
        submodule_search_locations=[str(repo_root)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    os.environ["ILAS_ADDON_MODULE"] = module_name
    return module


def main():
    load_addon()
    tests_dir = pathlib.Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(str(tests_dir), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
