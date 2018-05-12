# !/usr/bin/python
from setuptools import setup, find_packages
import flask_clova
setup_requires = []

dependency_links = [
]

setup(
    name='flask_clova',
    version=flask_clova.__version__,
    url='https://github.com/HwangWonYo/flask-clova.git',
    license='MIT License',
    description='A Python Library For CEK',
    author='wonyoHwang',
    author_email='hollal0726@gmail.com',
    packages=find_packages(exclude=['tests', 'samples', 'ncs']),
    # include_package_data=True,
    # install_requires=install_requires,
    # setup_requires=setup_requires,
    # dependency_links=dependency_links,
    keywords=['CEK', 'clova', 'extension', 'clova-extension-kit'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ]
)

