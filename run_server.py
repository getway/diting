#!/usr/bin/env python3
# coding: utf-8

import sys
import subprocess


if __name__ == '__main__':
    subprocess.call('python3 apps/manage.py runserver', shell=True,
                    stdin=sys.stdin, stdout=sys.stdout)
