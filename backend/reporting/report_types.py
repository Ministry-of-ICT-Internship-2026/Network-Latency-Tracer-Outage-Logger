from enum import Enum


class ReportFormat(str, Enum):
    PDF = "pdf"
    CSV = "csv"