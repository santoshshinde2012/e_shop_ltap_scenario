"""Shared fixtures. The default service reads the packaged E-Shop CSVs."""

from __future__ import annotations

import pytest

from e_shop_ltap.cli import build_service
from e_shop_ltap.inventory_service import ScenarioService
from e_shop_ltap.models import ScenarioReport


@pytest.fixture(scope="session")
def service() -> ScenarioService:
    return build_service()


@pytest.fixture(scope="session")
def report(service: ScenarioService) -> ScenarioReport:
    return service.build_report()
