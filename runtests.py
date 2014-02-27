#!/usr/bin/env python
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

import django
from django.conf import settings
from django.test.utils import get_runner


def main():
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(sys.argv[1:])
    sys.exit(failures)

if __name__ == '__main__':
    main()
