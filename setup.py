from setuptools import setup
from pip.req import parse_requirements

requirements = [
    str(ir.req) for ir in parse_requirements('requirements.txt', session=False)
]

setup(
    name='pyasar',
    version='1.0.0',
    author='Swen Kooij (Photonios)',
    author_email='photonios@outlook.com',
    description='Library for reading from Electron ASAR archives.',
    install_requires=requirements
)
