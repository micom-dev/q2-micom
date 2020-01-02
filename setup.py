from setuptools import setup, find_packages


setup(
    name="q2-micom",
    version="0.1.0",
    packages=find_packages(),
    package_data={"q2_micom": ["citations.bib", "assets"]},
    author="Christian Diener",
    author_email="cdiener (a) isbscience.org",
    description="Plugin for metabolic modeling of microbial communities.",
    license='Apache License 2.0',
    url="https://github.com/micom-dev/q2-micom",
    entry_points={
        'qiime2.plugins': ['q2-micom=q2_micom.plugin_setup:plugin']
    },
    zip_safe=False,
)
