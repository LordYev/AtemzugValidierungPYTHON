from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="AtemzugValidierung",
    version="1.3.6",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "runazv=project_module.main:main",
        ],
    },
    author="Yevgeniy Gennadijovic Palamarchuk",
    description="Programm zum validieren einzelner Atemzüge",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6"
)
