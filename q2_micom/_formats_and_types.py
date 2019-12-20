"""Formats and types for metabolic modeling."""

from qiime2.plugin import SemanticType
import qiime2.plugin.model as model


class SBMLFormat(model.TextFileFormat):
    """Represents an SBML file."""
    def _check_n_lines(self, n):
        """Crudely check if the file is SBML."""
        with open(str(self), mode="r") as xml_file:
            lines = xml_file.readlines(n).join("")
        return ".xml" in str(self).lower() and "<sbml" in lines.lower()

    def _validate_(self, level):
        record_map = {'min': 5, 'max': 100}
        return self._check_n_lines(self, record_map[level])


class SBMLDirectory(model.DirectoryFormat):
    sbml_files = model.FileCollection(r".+\.xml", format=SBMLFormat)

    @sbml_files.set_path_maker
    def sbml_path_maker(self, model_id):
        return "%s.xml" % model_id


class CommunityModelFormat(model.BinaryFileFormat):
    """Represents a pickled community model."""
    def _validate_(self, level):
        return str(self).lower().endswith(".pickle")


class CommunityModelDirectory(model.DirectoryFormat):
    model_files = model.FileCollection(r".+\.pickle",
                                       format=CommunityModelFormat)

    @model_files.set_path_maker
    def model_path_maker(self, model_id):
        return "%s.pickle" % model_id


class GrowthRates(model.TextFileFormat):
    def _validate_(self, level):
        header = open(str(self), mode="r").readline().split(",")
        return header == ["sample_id", "taxon", "reactions", "metabolites",
                          "abundance", "tradeoff", "growth_rate"]


class ExchangeFluxes(model.TextFileFormat):
    def _validate_(self, level):
        header = open(str(self), mode="r").readline().split(",")
        return header == ["sample_id", "taxon", "metabolite", "flux",
                          "direction"]


class MicomResultsDirectory(model.DirectoryFormat):
    growth_rates = model.File("growth_rates.csv", format=GrowthRates)
    exchange_fluxes = model.File("exchange_fluxes.csv", format=ExchangeFluxes)


class MicomMediumFile(model.TextFileFormat):
    def _validate_(self, level):
        header = open(str(self), mode="r").readline().split(",")
        return header == ["metabolite", "reaction", "flux"]


MicomMediumDirectory = model.SingleFileDirectoryFormat(
    "MicomMediumDirectory", "medium.csv", MicomMediumFile)

TradeoffResultsDirectory = model.SingleFileDirectoryFormat(
    "TradeoffResultsDirectory", "tradeoff.csv", GrowthRates)

MetabolicModels = SemanticType(
    "MetabolicModels",
    field_names="format",
    field_members=(SemanticType("SBML"),)
)

CommunityModels = SemanticType(
    "CommunityModels",
    field_names="format",
    field_members=(SemanticType("Pickle"),)
)

MicomResults = SemanticType("MicomResults")
TradeoffResults = SemanticType("TradeoffResults")
MicomMedium = SemanticType("MicomMedium")
