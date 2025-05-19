import importlib
import pkgutil
import wwwpy_plugins

for module_info in pkgutil.iter_modules(wwwpy_plugins.__path__):
    print(module_info)

print('importing modules')
for _, name, _ in pkgutil.iter_modules(wwwpy_plugins.__path__):
    module = importlib.import_module(f'wwwpy_plugins.{name}')
