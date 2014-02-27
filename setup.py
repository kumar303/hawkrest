from setuptools import setup, find_packages


setup(name='hawkrest',
      version='0.0.1',
      description="Hawk HTTP Authorization for Django Rest Framework",
      long_description='',
      author='Kumar McMillan',
      author_email='kumar.mcmillan@gmail.com',
      license='MPL 2.0 (Mozilla Public License)',
      url='https://github.com/kumar303/hawkrest',
      include_package_data=True,
      classifiers=[],
      packages=find_packages(exclude=['tests']),
      install_requires=['djangorestframework', 'mohawk'])
