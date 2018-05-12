# !/usr/bin/python
from setuptools import setup
import flask_clova

setup_requires = [
    'PyYAML==3.12',
    'Flask==0.12.1'
]

setup(
    name='flask_clova',
    version=flask_clova.__version__,
    url='https://github.com/HwangWonYo/flask-clova.git',
    license='MIT License',
    description='A Python Library For CEK',
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
    # install_requires=install_requires,
    # setup_requires=setup_requires,
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

