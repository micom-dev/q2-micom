"""Transformers for MICOM types."""

import pandas as pd
from q2_micom.plugin_setup import plugin
import q2_micom._formats_and_types as ft


@plugin.register_transformer
def _1(data: pd.DataFrame) -> ft.MicomMediumFile:
    mm = ft.MicomMediumFile()
    data.to_csv(str(mm), index=False)
    return mm


@plugin.register_transformer
def _2(mm: ft.MicomMediumFile) -> pd.DataFrame:
    return pd.read_csv(str(mm), index_col=False)


@plugin.register_transformer
def _3(data: pd.DataFrame) -> ft.ModelManifest:
    sbm = ft.SBMLManifest()
    data.to_csv(str(sbm), index=False)
    return sbm


@plugin.register_transformer
def _4(sbm: ft.ModelManifest) -> pd.DataFrame:
    return pd.read_csv(str(sbm), index_col=False)


@plugin.register_transformer
def _5(data: pd.DataFrame) -> ft.CommunityModelManifest:
    cmm = ft.CommunityModelManifest()
    data.to_csv(str(cmm), index=False)
    return cmm


@plugin.register_transformer
def _6(cmm: ft.CommunityModelManifest) -> pd.DataFrame:
    return pd.read_csv(str(cmm), index_col=False)


@plugin.register_transformer
def _7(data: pd.DataFrame) -> ft.GrowthRates:
    gr = ft.GrowthRates()
    data.to_csv(str(gr), index=False)
    return gr


@plugin.register_transformer
def _8(gr: ft.GrowthRates) -> pd.DataFrame:
    return pd.read_csv(str(gr), index_col=False)


@plugin.register_transformer
def _9(data: pd.DataFrame) -> ft.Fluxes:
    ef = ft.Fluxes()
    data.to_parquet(str(ef))
    return ef


@plugin.register_transformer
def _10(ef: ft.Fluxes) -> pd.DataFrame:
    return pd.read_parquet(str(ef))


@plugin.register_transformer
def _11(res: ft.MicomResultsDirectory) -> ft.MicomResultsData:
    return ft.MicomResultsData(
        exchange_fluxes=pd.read_parquet(str(res.exchange_fluxes.path_maker())),
        growth_rates=pd.read_csv(
            str(res.growth_rates.path_maker()), index_col=False)
    )
