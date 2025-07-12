from setuptools import setup, find_packages

setup(
    name="chatecho",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add your project's dependencies here, e.g.:
        # 'requests',
    ],
    entry_points={
        'console_scripts': [
            'chatecho=chatecho.cli:main',
        ],
    },
)