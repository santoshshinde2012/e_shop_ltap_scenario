"""Readings of the same inventory. Adding a fourth means adding a file here, nothing else."""

from __future__ import annotations

from .end_of_pipelines import EndOfPipelinesRule
from .name_keyword import NameKeywordRule
from .second_copy import SecondCopyRule

__all__ = ["EndOfPipelinesRule", "NameKeywordRule", "SecondCopyRule"]
