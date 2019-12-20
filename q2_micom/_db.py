"""Build a database of organism metabolic models."""

import pandas as pd
from qiime2 import Metadata
from q2_micom._formats_and_types import SBMLDirectory


def _make_db(manifest: Metadata, folder: str) -> (SBMLDirectory, pd.DataFrame):
    """Create a model database from a set of SBML files."""
