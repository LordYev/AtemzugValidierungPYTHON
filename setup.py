from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="AtemzugValidierung",
    version="1.0",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'run_azv_main=project_module.main:main',
        ],
    },
    author="Yevgeniy Gennadijovic Palamarchuk",
    description="Programm zum validieren einzelner Atemzüge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6'
)