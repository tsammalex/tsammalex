from setuptools import setup, find_packages


requires = [
    'requests',
    'purl',
    'pycountry==1.20',
    'flickrapi',
    'python-dateutil',
    'BeautifulSoup4',
    'shapely',
    'clldutils>=1.4.3',
    'python-levenshtein',
    'attrs',
    'cdstarcat',
    'tqdm',
]

setup(
    name='pytsammalex',
    version='0.1.0',
    description='data for the tsammalex site',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    author='',
    author_email='',
    url='',
    keywords='data linguistics',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'console_scripts': ['tsammalex=pytsammalex.cli:main'],
    },
    tests_require=[],
    test_suite="pytsammalex")
