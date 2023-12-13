#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import MagicMock, mock_open, patch

from ops.model import Unit
from ops.testing import Harness

from charm import PostgresqlOperatorCharm
from relations.async_replication import _get_pod_ip


class TestPostgreSQLAsyncReplication(unittest.TestCase):
    @patch("charm.KubernetesServicePatch", lambda x, y: None)
    def setUp(self):
        self.harness = Harness(PostgresqlOperatorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.charm = self.harness.charm

        # Setup Async Replication wrapper.
        self.async_manager = self.charm.async_manager

    def test_get_pod_ip(self):
        # Set up a mock for the `open` method.
        mock = mock_open()
        # Patch the `open` method with our mock.
        with patch("builtins.open", mock, create=True):
            handle1 = MagicMock()
            handle1.__enter__.return_value.read.return_value = """# Kubernetes-managed hosts file.
127.0.0.1\tlocalhost
::1 localhost\tip6-localhost\tip6-loopback
fe00::0\tip6-localnet
fe00::0\tip6-mcastprefix
fe00::1\tip6-allnodes
fe00::2\tip6-allrouters
10.1.123.23\tpostgresql-k8s-0.postgresql-k8s-endpoints.dev.svc.cluster.local\tpostgresql-k8s-0
"""
            handle1.__exit__.return_value = False
            handle2 = MagicMock()
            handle2.__enter__.return_value.read.return_value = """postgresql-k8s-0
"""
            handle2.__exit__.return_value = False
            mock.side_effect = (handle1, handle2)
            self.assertEqual(_get_pod_ip(), "10.1.123.23")

    def test_endpoint(self):
        # Test when the relation is not set yet.
        self.assertIsNone(self.async_manager.endpoint)

        # Test when the async primary relation is set.
        print(self.charm.async_manager.relation_set)
        # async_primary_rel_id = self.harness.add_relation("async-primary", self.charm.app.name)
        # self.harness.add_relation_unit(async_primary_rel_id, f"{self.charm.app.name}/0")
        # relation = self.harness.model.get_relation("async-primary", async_primary_rel_id)
        # self.charm.on.async_primary_relation_created.emit(relation)
        # self.harness.reset_planned_units()
        # print(self.charm.async_manager.relation_set)
        # self.assertEqual(self.charm.async_manager.endpoint, "postgresql-k8s-endpoints")
        #
        # # Test when the async replica relation is set.
        # self.harness.remove_relation(async_primary_rel_id)
        # self.harness.add_relation("async-replica", self.charm.app.name)
        # self.assertEqual(self.async_manager.endpoint, "postgresql-k8s-endpoints")

    def test_standby_endpoints(self):
        # Test when the relation is not set yet.
        self.assertEqual(self.async_manager.standby_endpoints(), set())

        # Test when the async primary relation is set.

        # Test when the async replica relation is set.

    def test_get_primary_data(self):
        pass

    def test_all_units(self):
        rel_id = self.harness.add_relation("async-primary", self.charm.app.name)
        relation = self.harness.model.get_relation("async-primary", rel_id)
        self.assertEqual(self.async_manager._all_units(relation), {self.charm.unit})

        second_unit = Unit(f"{self.charm.app}/1", None, self.harness.charm.app._backend, {})
        self.harness.add_relation_unit(rel_id, second_unit.name)
        # self.harness.set_planned_units(2)
        self.assertEqual(self.async_manager._all_units(relation), {self.charm.unit, second_unit})

    def test_all_replica_published_pod_ips(self):
        pass

    def test_on_departure(self):
        pass

    def test_on_primary_changed(self):
        pass

    def test_on_standby_changed(self):
        pass

    def test_on_coordination_request(self):
        pass

    def test_on_coordination_approval(self):
        pass

    def test_get_primary_candidates(self):
        # Test when the relation is not set yet.
        self.assertEqual(self.async_manager._get_primary_candidates(), [])

        # Test when the async primary relation is set.
        self.harness.add_relation("async-primary", self.charm.app.name)

    def test_check_if_primary_already_selected(self):
        pass

    def test_on_promote_standby_cluster(self):
        pass
