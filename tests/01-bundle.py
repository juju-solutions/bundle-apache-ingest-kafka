#!/usr/bin/env python3

import amulet
import os
import unittest
import yaml


class TestBundle(unittest.TestCase):
    bundle_file = os.path.join(os.path.dirname(__file__), '..', 'bundle.yaml')

    @classmethod
    def setUpClass(cls):
        cls.d = amulet.Deployment(series='trusty')
        with open(cls.bundle_file) as f:
            bun = f.read()
        bundle = yaml.safe_load(bun)
        cls.d.load(bundle)
        cls.d.setup(timeout=1800)
        cls.d.sentry.wait_for_messages({'flume-hdfs': 'Ready'}, timeout=1800)
        cls.hdfs = cls.d.sentry['namenode'][0]
        cls.yarn = cls.d.sentry['resourcemanager'][0]
        cls.slave = cls.d.sentry['slave'][0]
        cls.kafka = cls.d.sentry['kafka'][0]

    def test_components(self):
        """
        Confirm that all of the required components are up and running.
        """
        hdfs, retcode = self.hdfs.run("pgrep -a java")
        yarn, retcode = self.yarn.run("pgrep -a java")
        slave, retcode = self.slave.run("pgrep -a java")
        kafka, retcode = self.kafka.run("pgrep -a java")

        assert 'NameNode' in hdfs, "NameNode not started"
        assert 'NameNode' not in yarn, "NameNode should not be running on resourcemanager"
        assert 'NameNode' not in slave, "NameNode should not be running on slave"
        assert 'NameNode' not in kafka, "NameNode should not be running on kafka"

        assert 'ResourceManager' in yarn, "ResourceManager not started"
        assert 'ResourceManager' not in hdfs, "ResourceManager should not be running on namenode"
        assert 'ResourceManager' not in slave, "ResourceManager should not be running on slave"
        assert 'ResourceManager' not in kafka, "ResourceManager should not be running on kafka"

        assert 'JobHistoryServer' in yarn, "JobHistoryServer not started"
        assert 'JobHistoryServer' not in hdfs, "JobHistoryServer should not be running on namenode"
        assert 'JobHistoryServer' not in slave, "JobHistoryServer should not be running on slave"
        assert 'JobHistoryServer' not in kafka, "JobHistoryServer should not be running on kafka"

        assert 'NodeManager' in slave, "NodeManager not started"
        assert 'NodeManager' not in yarn, "NodeManager should not be running on resourcemanager"
        assert 'NodeManager' not in hdfs, "NodeManager should not be running on namenode"
        assert 'NodeManager' not in kafka, "NodeManager should not be running on kafka"

        assert 'DataNode' in slave, "DataServer not started"
        assert 'DataNode' not in yarn, "DataNode should not be running on resourcemanager"
        assert 'DataNode' not in hdfs, "DataNode should not be running on namenode"
        assert 'DataNode' not in kafka, "DataNode should not be running on kafka"

        assert 'Kafka' in kafka, 'Kafka should be running on kafka'

    def test_hdfs(self):
        """Smoke test validates mkdir, ls, chmod, and rm on the hdfs cluster."""
        unit_name = self.hdfs.info['unit_name']
        uuid = self.d.action_do(unit_name, 'smoke-test')
        result = self.d.action_fetch(uuid)
        # hdfs smoke-test sets outcome=success on success
        if (result['outcome'] != "success"):
            error = "HDFS smoke-test failed"
            amulet.raise_status(amulet.FAIL, msg=error)

    def test_yarn(self):
        """Smoke test validates teragen/terasort."""
        unit_name = self.yarn.info['unit_name']
        uuid = self.d.action_do(unit_name, 'smoke-test')
        result = self.d.action_fetch(uuid)
        # yarn smoke-test only returns results on failure; if result is not
        # empty, the test has failed and has a 'log' key
        if result:
            error = "YARN smoke-test failed: %s" % result['log']
            amulet.raise_status(amulet.FAIL, msg=error)

    def test_kafka(self):
        """Smoke test validates create/list/delete of a Kafka topic."""
        unit_name = self.kafka.info['unit_name']
        uuid = self.d.action_do(unit_name, 'smoke-test')
        result = self.d.action_fetch(uuid)
        # kafka smoke-test sets outcome=success on success
        if (result['outcome'] != "success"):
            error = "Kafka smoke-test failed"
            amulet.raise_status(amulet.FAIL, msg=error)


if __name__ == '__main__':
    unittest.main()
