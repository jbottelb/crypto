from setuptools import setup, find_packages

with open("README.md") as f:
	readme = f.read()

with open("LICENSE") as f:
	license = f.read()

setup(
	name='JBcoin',
	version='0.1.0',
	description="Cryptocurrency",
	long_description=readme,
	author="Josh Bottelberghe",
	author_email="jbottelb@nd.edu",
	url="https://github.com/jbottelb/crypto/tree/main",
	license=license,
	packages=find_packages(exclude=('tests', 'docs', 'data'))
)
