import importlib
import pkgutil

_loaded = False


def load_tools():
    global _loaded

    if _loaded:
        return

    _loaded = True

    package_name = "minicode.tools"
    package = __import__(package_name, fromlist=[""])

    for _, module_name, _ in pkgutil.walk_packages(
        package.__path__, package_name + "."
    ):
        importlib.import_module(module_name)
