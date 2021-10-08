import q2_micom._transform as mt
from micom.workflows import GrowthResults
import pandas as pd


test_results = GrowthResults(
    pd.DataFrame(
        {
            "sample_id": [1, 2],
            "taxon": ["Bacteroides", "Firmicutes"],
            "reactions": [1243, 2345],
            "metabolites": [2345, 3456],
            "abundance": [0.7, 0.3],
            "tradeoff": [0.5, 0.5],
            "growth_rate": [0.2, 0.1],
        },
        index=range(2),
    ),
    pd.DataFrame(
        {
            "sample_id": [1, 2],
            "reaction": ["EX_ac_e", "EX_but_e"],
            "metabolite": ["ac_e", "but_e"],
            "flux": [0.2, 10],
            "direction": ["export", "export"],
        },
        index=range(2),
    ),
    pd.DataFrame(
        {
            "reaction": ["EX_ac_e", "EX_but_e"],
            "metabolite": ["ac_e", "but_e"],
            "description": ["acetate", "butyrate"],
        },
        index=range(2),
    ),
)


def test_ids_are_strings():
    results_dir = mt._15(test_results)
    read = mt._14(results_dir)
    assert read.growth_rates.sample_id.dtype.kind == "O"
    assert read.exchanges.sample_id.dtype.kind == "O"
