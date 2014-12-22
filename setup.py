from setuptools import setup, find_packages


setup(name='tsammalexdata',
      version='0.0',
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
      install_requires=['requests', 'purl', 'pycountry'],
      tests_require=[],
      test_suite="tsammalexdata")
