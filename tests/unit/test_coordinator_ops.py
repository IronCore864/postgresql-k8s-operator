#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import patch

from ops.testing import Harness

from charm import PostgresqlOperatorCharm


class TestCoordinatedOpsManager(unittest.TestCase):
    @patch("charm.KubernetesServicePatch", lambda x, y: None)
    def setUp(self):
        self.harness = Harness(PostgresqlOperatorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.charm = self.harness.charm

        # Setup Coordinated Ops Manager wrapper.
        self.restart_coordinator = self.charm.async_manager.restart_coordinator

    def test_under_coordination(self):
        pass

    def test_coordinate(self):
        pass

    def test_acknowledge(self):
        pass

    def test_on_relation_changed(self):
        pass
