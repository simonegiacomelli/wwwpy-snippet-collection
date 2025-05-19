import sys
from pathlib import Path


def do_dyn():
    print('')
    dynamic = (Path(__file__) / '../../../../dynamic').resolve()
    print(f'do_dyn, adding dynamic path: {dynamic}')
    print('')
    assert dynamic.exists()

    sys.path.append(str(dynamic))
