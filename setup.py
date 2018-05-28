# !/usr/bin/python
from setuptools import setup
import flask_clova

setup_requires = [
    'PyYAML',
    'flask'
]

setup(
    name='flask_clova',
    version=flask_clova.__version__,
    url='https://github.com/HwangWonYo/flask-clova.git',
    license='MIT License',
    description='A Python Library For CEK',
    long_description=__doc__,
    author='wonyoHwang',
    author_email='hollal0726@gmail.com',
    packages=['flask_clova'],
    install_requires=setup_requires,
    test_requires=[
        'mock',
        'requests'
    ],
    test_suite='tests',
    # include_package_data=True,
    # dependency_links=dependency_links,
    keywords=['CEK', 'clova', 'extension', 'clova-extension-kit'],
    classifiers=[
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ]
)

