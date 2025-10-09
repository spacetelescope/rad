from __future__ import annotations

from typing import TYPE_CHECKING

from deepdiff import DeepDiff

if TYPE_CHECKING:
    from typing import Any


__all__ = ["diff"]


def diff(current_schemas: dict[str, dict[str, dict[str, Any]]], main_schemas: dict[str, dict[str, dict[str, Any]]]) -> DeepDiff:
    """
    Find the differences between two sets of archive schemas.
    """
    return DeepDiff(main_schemas, current_schemas, ignore_order=True)
