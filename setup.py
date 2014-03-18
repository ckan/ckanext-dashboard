from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
        name='ckanext-dashboard',
        version=version,
        description="Dashboard extension for CKAN",
        long_description="""\
        """,
        classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        keywords='',
        author='okfn',
        author_email='info@okfn.org',
        url='',
        license='',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        namespace_packages=['ckanext', 'ckanext.dashboard'],
        include_package_data=True,
        zip_safe=False,
        install_requires=[
                # -*- Extra requirements: -*-
        ],
        entry_points=\
        """
        [ckan.plugins]
        # Add plugins here
    dashboard_preview=ckanext.dashboard.plugin:DashboardView
        """,
)
