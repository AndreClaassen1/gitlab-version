'''access to a number of test constants
'''

import os
from pathlib import Path

def _get_test_path() -> Path:
    '''get the test path
    '''
    test_path = Path(os.path.abspath(__file__)) / \
        '..' / '..' / '..' / 'tests'
    return test_path


def get_scratch_path():
    ''' get the path to the test scratch dir
    Create the directory if it does not exist.
    '''
    scratch_path = _get_test_path() / 'scratch'
    scratch_path = scratch_path.resolve()
    if not scratch_path.exists():
        scratch_path.mkdir(parents=True, exist_ok=True)
    return str(scratch_path)


def get_testdata_path():
    ''' get the path to the test testdata dir
    '''
    testdata_path = _get_test_path() / 'testdata'
    return str(testdata_path.resolve())