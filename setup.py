
"""Setup file for q2-micom."""
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name="q2-micom",
    version="0.10.0",
    packages=find_packages(),
    package_data={"q2_micom": ["citations.bib", "assets/templates/*.html"]},
    author="Christian Diener",
    author_email="cdiener@isbscience.org",
    description="Plugin for metabolic modeling of microbial communities.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="Apache License 2.0",
    url="https://github.com/micom-dev/q2-micom",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # What does your project relate to?
    keywords="microbiome modeling metabolism community",
    entry_points={
        'qiime2.plugins': ['q2-micom=q2_micom.plugin_setup:plugin']
    },
    zip_safe=False,
    install_requires=[
        "cobra>=0.18.1",
        "pandas>=1.0",
        "loguru>=0.3.2",
        "micom==0.18.7",
        "jinja2>=2.10.3",
        "qiime2>=2020.6.0"
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": [""],
        "test": ["coverage", "pytest", "pytest-cov", "flake8"],
    },
)
