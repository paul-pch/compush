from setuptools import setup, find_packages

setup(
    name="compush",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "compush=compush.main:main",
        ],
    },
    install_requires=[
        "mistralai==1.0.1",
        "typer==0.12.3",
        "rich==13.7.1",
    ],
    python_requires=">=3.8",
)
