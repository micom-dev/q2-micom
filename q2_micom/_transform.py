"""Transformers for MICOM types."""

import pandas as pd
from q2_micom.plugin_setup import plugin
import q2_micom._formats_and_types as ft


@plugin.register_transformer
def _1(data: pd.DataFrame) -> ft.MicomMediumFile:
    mm = ft.MicomMediumFile()
    data.to_csv(str(mm))
    return mm


@plugin.register_transformer
def _2(mm: ft.MicomMediumFile) -> pd.DataFrame:
    return pd.read_csv(str(mm), index_col="reaction")
