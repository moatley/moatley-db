from distutils.core import setup

from os import listdir
from os.path import join

version = '$Version: trunk$'[9:-1].strip()

setup(
    name="moatley-db",
    packages=[
        'moatley',
        'moatley.db',
        'moatley.db.fields',
        ],
    package_data={
    },
    scripts=[
    ],
    version=version,
    author="Johan Jonkers",
    author_email="moatley@moatley.net",
    description="Database Interface with python descriptors",
    long_description="Database Interface with python descriptors",
    license="GNU Public License",
    platforms="all",
)
