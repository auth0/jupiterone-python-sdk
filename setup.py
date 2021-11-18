# Copyright (c) 2020 Auth0

from setuptools import setup, find_packages

install_reqs = [
    'requests',
    'retrying'
]

setup(name='jupiterone',
      version='0.2.0',
      description='A Python client for the JupiterOne API',
      license='MIT License',
      author='George Vauter',
      author_email='george.vauter@auth0.com',
      maintainer='Auth0',
      url='https://github.com/auth0/jupiterone-python-sdk',
      install_requires=install_reqs,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Security',
      ],
      packages=find_packages()
)
