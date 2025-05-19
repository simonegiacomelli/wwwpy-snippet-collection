import importlib
import pkgutil
import wwwpy_plugins
from wwwpy_plugins_discovery import dyn


def print_info():
    print('print_info ' + '-' * 20)
    mod_infos = list(pkgutil.iter_modules(wwwpy_plugins.__path__))
    print(f'found {len(mod_infos)} modules:')

    for mi in mod_infos:
        print(f'  {mi.name} ({mi.module_finder})')

    print('\nimporting modules:')
    for _, name, _ in mod_infos:
        print(f'  importing {name}')
        module = importlib.import_module(f'wwwpy_plugins.{name}')
    print('')
    print('print_info END ' + '-' * 20)


print_info()
dyn.do_dyn()
print_info()
