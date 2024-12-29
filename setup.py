from setuptools import setup, find_packages

setup(
    name="ragchat",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "ragchat=ragchat.main:main",
        ],
    },
)