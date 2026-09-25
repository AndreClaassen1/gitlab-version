import sys
import unittest

import xmlrunner

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    with open('test_reports.xml', 'wb') as output:
        runner = xmlrunner.XMLTestRunner(
            output=output, verbosity=2)  # type: ignore
        result = runner.run(suite)
        # Überprüfe das Ergebnis und setze den Exit-Code
        if not result.wasSuccessful():
            sys.exit(1)
