"""Compliance module enums."""

from enum import Enum


class FrameworkType(str, Enum):
    """Supported compliance frameworks."""

    NIST_CSF = "nist_csf"
    NIST_800_53 = "nist_800_53"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    CIS = "cis"
    MITRE_ATTCK = "mitre_attck"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"


class ComplianceStatus(str, Enum):
    """Control compliance status."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


__all__ = ["FrameworkType", "ComplianceStatus"]
