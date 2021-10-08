"""Build a database of organism metabolic models."""

from micom.workflows import build_database
import os
from qiime2 import Metadata
from q2_micom._formats_and_types import JSONDirectory


def db(meta: Metadata, rank: str = "genus", threads: int = 1) -> JSONDirectory:
    """Create a model database from a set of SBML files."""
    meta = meta.to_dataframe()
    json_dir = JSONDirectory()
    path = str(json_dir.json_files.path_maker(model_id="dummy"))
    path = os.path.dirname(path)
    meta = build_database(meta, path, rank, threads, compress=False)
    os.rename(os.path.join(path, "manifest.csv"), json_dir.manifest.path_maker())
    return json_dir
