from setuptools import setup, find_packages

def get_requirements(path: str):
    return open(path).read().splitlines()

setup(
    name='WAVTactilTransformer',
    version='0.0.1',
    packages=find_packages(where="src"),
    install_requires=get_requirements('requirements.txt'),
)