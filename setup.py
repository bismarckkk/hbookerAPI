from os import path as os_path
from setuptools import setup, find_packages
import hbookerAPI

this_directory = os_path.abspath(os_path.dirname(__file__))


def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


setup(
    name='hbookerAPI',
    python_requires='>=3.4.0',
    version=hbookerAPI.__version__,
    description="刺猬猫/欢乐书客客户端API实现.",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    author="bismarck",
    author_email='wsgrbsm@gmail.com',
    url='https://github.com/abc55660745/hbookerAPI',
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,
    license="MIT",
    keywords=['hbooker', 'ciweimao'],
)
