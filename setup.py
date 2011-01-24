#!/usr/bin/env python

from distutils.core import setup

setup(
    name='tweeeet',
    version='0.1',
	description='twitter client in pygtk',
	author='Mike Qin',
	package_data = {'tweeeet.ui': ['data/*']},
	packages=['tweeeet', 'tweeeet.ui', 'tweeeet.core'],
    scripts=['scripts/tweeeet']
    )
