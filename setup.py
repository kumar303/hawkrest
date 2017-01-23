from setuptools import setup, find_packages


setup(name='hawkrest',
      version='0.0.10',
      description="Hawk HTTP Authorization for Django Rest Framework",
      long_description='',
      author='Kumar McMillan',
      author_email='kumar.mcmillan@gmail.com',
      license='MPL 2.0 (Mozilla Public License)',
      url='https://github.com/kumar303/hawkrest',
      include_package_data=True,
      classifiers=[
          'Framework :: Django',
          'Framework :: Django :: 1.8',
          'Framework :: Django :: 1.9',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet :: WWW/HTTP',
      ],
      packages=find_packages(exclude=['tests']),
      install_requires=['djangorestframework', 'mohawk>=0.3.3'])
