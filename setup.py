from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="neurobit_licitacion_classifier",
    version="0.1.0",
    description="Módulo de clasificación de información para procesos de licitación en construcción",
    long_description=README,
    long_description_content_type="text/markdown",
    author="David Sandoval",
    author_email="daelsand@espol.edu.ec",
    url="https://github.com/davexat/HackIAthon_neurobit_licitacion",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="licitacion clasificacion NLP spaCy sklearn",
    license="MIT",
)