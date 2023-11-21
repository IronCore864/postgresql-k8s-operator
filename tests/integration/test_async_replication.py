#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.
import logging
from asyncio import gather

import pytest as pytest
from juju.model import Model
from pytest_operator.plugin import OpsTest

from tests.integration.helpers import (
    build_and_deploy, DATABASE_APP_NAME,
)

logger = logging.getLogger(__name__)


@pytest.mark.abort_on_fail
async def test_async_replication(ops_test: OpsTest) -> None:
    """Build and deploy two PostgreSQL cluster in two separate models to test async replication."""
    first_model = ops_test.model
    second_model_name = f"{first_model.info.name}-other"
    await (await ops_test.model.get_controller()).add_model(second_model_name)
    second_model = Model()
    await second_model.connect(model_name=second_model_name)
    async with ops_test.fast_forward():
        await build_and_deploy(ops_test, 3, wait_for_idle=False, model=first_model)
        await build_and_deploy(ops_test, 3, wait_for_idle=False, model=second_model)
    await gather(
        first_model.wait_for_idle(
            apps=[DATABASE_APP_NAME],
            status="active",
        ),
        second_model.wait_for_idle(
            apps=[DATABASE_APP_NAME],
            status="active",
        )
    )
