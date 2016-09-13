#!/usr/bin/env python
import os
import sys
from eshot_api.settings import DEBUG

if __name__ == "__main__":
    if DEBUG == True:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eshot_api.conf.dev")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eshot_api.conf.prod")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
