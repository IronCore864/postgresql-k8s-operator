#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
import time

import pytest
from pytest_operator.plugin import OpsTest

from tests.integration.ha_tests.helpers import (
    METADATA,
    app_name,
    change_master_start_timeout,
    count_writes,
    get_primary,
    kill_process,
    postgresql_ready,
)

# PATRONI_PROCESS = "/usr/bin/python3 /usr/local/bin/patroni /var/lib/postgresql/data/patroni.yml"
POSTGRESQL_PROCESS = "postgres"


@pytest.mark.abort_on_fail
@pytest.mark.ha_tests
async def test_build_and_deploy(ops_test: OpsTest, continuous_writes) -> None:
    """Build and deploy three unit of PostgreSQL."""
    # It is possible for users to provide their own cluster for HA testing. Hence, check if there
    # is a pre-existing cluster.
    if await app_name(ops_test):
        return

    charm = await ops_test.build_charm(".")
    async with ops_test.fast_forward():
        await ops_test.model.deploy(
            charm,
            resources={
                "postgresql-image": METADATA["resources"]["postgresql-image"]["upstream-source"]
            },
            num_units=3,
            trust=True,
        )
        await ops_test.model.wait_for_idle(status="active", timeout=1000)


@pytest.mark.ha_tests
async def test_kill_db_processes(ops_test) -> None:
    # locate primary unit
    app = await app_name(ops_test)
    primary_name = await get_primary(ops_test, app)

    await ops_test.model.relate(app, "application")
    await ops_test.model.wait_for_idle(status="active", timeout=1000)

    print(f"primary_name: {primary_name}")
    await change_master_start_timeout(ops_test, 0)
    await kill_process(ops_test, primary_name, POSTGRESQL_PROCESS, kill_code="SIGKILL")
    await change_master_start_timeout(ops_test, 300)

    # verify new writes are continuing by counting the number of writes before and after a 5 second
    # wait
    writes = await count_writes(ops_test)
    time.sleep(5)
    more_writes = await count_writes(ops_test)
    print(writes)
    print(more_writes)
    assert more_writes > writes, "writes not continuing to DB"

    # sleep for twice the median election time
    time.sleep(30 * 2)

    # verify that db service got restarted and is ready
    assert await postgresql_ready(ops_test, primary_name)

    # verify that a new primary gets elected (ie old primary is secondary)
    new_primary_name = await get_primary(ops_test, app)
    assert new_primary_name != primary_name