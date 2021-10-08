"""Formats and types for metabolic modeling."""

from collections import namedtuple
import pandas as pd
from qiime2.plugin import SemanticType
import qiime2.plugin.model as model

REQ_FIELDS = pd.Series(
    ["file", "kingdom", "phylum", "class", "order", "family", "genus", "species"]
)


class SBMLFormat(model.TextFileFormat):
    """Represents an SBML file."""

    def _check_n_lines(self, n):
        """Crudely check if the file is SBML."""
        with open(str(self), mode="r") as xml_file:
            lines = "".join(xml_file.readlines(n))
        return ".xml" in str(self).lower() and "<sbml" in lines.lower()

    def _validate_(self, level):
        record_map = {"min": 5, "max": 100}
        return self._check_n_lines(record_map[level])


class JSONFormat(model.TextFileFormat):
    """Represents a JSON file."""

    def _check_n_lines(self, n):
        """Crudely check if the file is SBML."""
        with open(str(self), mode="r") as xml_file:
            lines = "".join(xml_file.readlines(n))
        return ".xml" in str(self).lower() and "metabolites" in lines.lower()

    def _validate_(self, level):
        record_map = {"min": 5, "max": 100}
        return self._check_n_lines(record_map[level])


class ModelManifest(model.TextFileFormat):
    """Represents an SBML file."""

    def _validate_(self, level):
        header = open(str(self), mode="r").readline().split(",")
        return REQ_FIELDS.isin(header).all()


class SBMLDirectory(model.DirectoryFormat):
    manifest = model.File("manifest.csv", format=ModelManifest)
    sbml_files = model.FileCollection(r".+\.xml", format=SBMLFormat)

    @sbml_files.set_path_maker
    def sbml_path_maker(self, model_id):
        return "%s.xml" % model_id


class JSONDirectory(model.DirectoryFormat):
    manifest = model.File("manifest.csv", format=ModelManifest)
    json_files = model.FileCollection(r".+\.json", format=JSONFormat)

    @json_files.set_path_maker
    def sbml_path_maker(self, model_id):
        return "%s.json" % model_id


class CommunityModelFormat(model.BinaryFileFormat):
    """Represents a pickled community model."""

    def _validate_(self, level):
        return str(self).lower().endswith(".pickle")


class CommunityModelManifest(model.TextFileFormat):
    """Represents a manifets for community models."""

    def _validate_(self, level):
        header = open(str(self), mode="r").readline().split(",")
        return "sample_id" in header


class CommunityModelDirectory(model.DirectoryFormat):
    manifest = model.File("manifest.csv", format=CommunityModelManifest)
    model_files = model.FileCollection(r".+\.pickle", format=CommunityModelFormat)

    @model_files.set_path_maker
    def model_path_maker(self, model_id):
        return "%s.pickle" % model_id


class GrowthRates(model.TextFileFormat):
    def _validate_(self, level):
        header = open(str(self), mode="r").readline().split(",")
        return header == [
            "sample_id",
            "taxon",
            "reactions",
            "metabolites",
            "abundance",
            "tradeoff",
            "growth_rate",
        ]


class Fluxes(model.TextFileFormat):
    def _validate_(self, level):
        return str(self).endswith(".csv")


class Annotations(model.TextFileFormat):
    def _validate_(self, level):
        header = open(str(self), mode="r").readline().split(",")
        return header == ["reaction", "metabolite", "description"]


class MicomResultsDirectory(model.DirectoryFormat):
    growth_rates = model.File("growth_rates.csv", format=GrowthRates)
    exchange_fluxes = model.File("exchange_fluxes.csv", format=Fluxes)
    annotations = model.File("annotations.csv", format=Annotations)


class MicomMediumFile(model.TextFileFormat):
    def _validate_(self, level):
        header = open(str(self), mode="r").readline().split(",")
        return header == ["metabolite", "reaction", "flux"]


MicomMediumDirectory = model.SingleFileDirectoryFormat(
    "MicomMediumDirectory", "medium.csv", MicomMediumFile
)

TradeoffResultsDirectory = model.SingleFileDirectoryFormat(
    "TradeoffResultsDirectory", "tradeoff.csv", GrowthRates
)

SBML = SemanticType("SBML")
Pickle = SemanticType("Pickle")
JSON = SemanticType("JSON")

MetabolicModels = SemanticType(
    "MetabolicModels", field_names="format", field_members={"format": (SBML, JSON)}
)

CommunityModels = SemanticType(
    "CommunityModels", field_names="format", field_members={"format": (Pickle,)}
)

MicomResults = SemanticType("MicomResults")
TradeoffResults = SemanticType("TradeoffResults")

Global = SemanticType("Global")
PerSample = SemanticType("PerSample")
MicomMedium = SemanticType(
    "MicomMedium", field_names="type", field_members={"type": (Global, PerSample)}
)


MicomResultsData = namedtuple("MicomResultsData", ["growth_rates", "exchange_fluxes"])
