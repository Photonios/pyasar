from setuptools import setup
from pip.req import parse_requirements

requirements = [
    str(ir.req) for ir in parse_requirements('requirements.txt', session=False)
]

setup(
    name='pyasar',
    packages=['asar'],
    version='1.0.7',
    author='Swen Kooij (Photonios)',
    author_email='photonios@outlook.com',
    description='Library for working with Electron\'s ASAR archives.',
    long_description=open('README.rst').read(),
    url='https://github.com/Photonios/pyasar.git',
    keywords=['asar', 'electron', 'pyasar'],
    install_requires=requirements
)
