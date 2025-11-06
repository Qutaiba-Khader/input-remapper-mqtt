# -*- coding: utf-8 -*-
# input-remapper - GUI for device specific keyboard mappings
# Copyright (C) 2025 sezanzeb <b8x45ygc9@mozmail.com>
#
# This file is part of input-remapper.
#
# input-remapper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# input-remapper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with input-remapper.  If not, see <https://www.gnu.org/licenses/>.

"""Tests for MQTT client module."""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

from inputremapper.mqtt_client import MQTTConfig, MQTTClient


class TestMQTTConfig(unittest.TestCase):
    """Test MQTT configuration handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "mqtt_config.json")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_mqtt_config_defaults(self):
        """Test MQTTConfig default values."""
        config = MQTTConfig()
        self.assertEqual(config.broker, "192.168.1.160")
        self.assertEqual(config.port, 1883)
        self.assertEqual(config.topic, "key_remap/events")
        self.assertEqual(config.qos, 1)
        self.assertFalse(config.retain)
        self.assertIsNone(config.default_device_name)
        self.assertIsNone(config.ha_url)

    def test_mqtt_config_custom_values(self):
        """Test MQTTConfig with custom values."""
        config = MQTTConfig(
            broker="test.broker.com",
            port=8883,
            username="testuser",
            password="testpass",
            topic="test/topic",
            qos=2,
            retain=True,
            default_device_name="test_device",
            ha_url="http://localhost:8123"
        )
        self.assertEqual(config.broker, "test.broker.com")
        self.assertEqual(config.port, 8883)
        self.assertEqual(config.username, "testuser")
        self.assertEqual(config.password, "testpass")
        self.assertEqual(config.topic, "test/topic")
        self.assertEqual(config.qos, 2)
        self.assertTrue(config.retain)
        self.assertEqual(config.default_device_name, "test_device")
        self.assertEqual(config.ha_url, "http://localhost:8123")

    def test_load_config_from_file(self):
        """Test loading configuration from file."""
        config_data = {
            "broker": "test.broker.com",
            "port": 8883,
            "username": "testuser",
            "password": "testpass",
            "topic": "test/topic",
            "qos": 2,
            "retain": True,
            "default_device_name": "test_device",
            "ha_url": "http://localhost:8123"
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        config = MQTTConfig.load_from_file(self.config_path)
        self.assertEqual(config.broker, "test.broker.com")
        self.assertEqual(config.port, 8883)
        self.assertEqual(config.ha_url, "http://localhost:8123")

    def test_load_config_missing_file(self):
        """Test error when config file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            MQTTConfig.load_from_file("/nonexistent/path.json")

    def test_load_config_invalid_json(self):
        """Test error with invalid JSON."""
        with open(self.config_path, "w") as f:
            f.write("invalid json {{{")

        with self.assertRaises(ValueError) as cm:
            MQTTConfig.load_from_file(self.config_path)
        self.assertIn("Invalid JSON", str(cm.exception))

    def test_load_config_missing_required_fields(self):
        """Test error with missing required fields."""
        config_data = {
            "broker": "test.broker.com",
            # Missing port, username, password
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        with self.assertRaises(ValueError) as cm:
            MQTTConfig.load_from_file(self.config_path)
        self.assertIn("Missing required fields", str(cm.exception))

    def test_save_config_to_file(self):
        """Test saving configuration to file."""
        config = MQTTConfig(
            broker="test.broker.com",
            port=8883,
            username="testuser",
            password="testpass",
            ha_url="http://localhost:8123"
        )

        config.save_to_file(self.config_path)

        # Load it back and verify
        with open(self.config_path, "r") as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data["broker"], "test.broker.com")
        self.assertEqual(saved_data["port"], 8883)
        self.assertEqual(saved_data["ha_url"], "http://localhost:8123")

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = MQTTConfig(
            broker="test.broker.com",
            port=8883,
            username="testuser",
            password="testpass",
            topic="test/topic",
            qos=2,
            retain=True,
            default_device_name="test_device",
            ha_url="http://localhost:8123"
        )

        config_dict = config.to_dict()
        self.assertEqual(config_dict["broker"], "test.broker.com")
        self.assertEqual(config_dict["port"], 8883)
        self.assertEqual(config_dict["username"], "testuser")
        self.assertEqual(config_dict["password"], "testpass")
        self.assertEqual(config_dict["topic"], "test/topic")
        self.assertEqual(config_dict["qos"], 2)
        self.assertTrue(config_dict["retain"])
        self.assertEqual(config_dict["default_device_name"], "test_device")
        self.assertEqual(config_dict["ha_url"], "http://localhost:8123")


class TestMQTTClient(unittest.TestCase):
    """Test MQTT client functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MQTTConfig(
            broker="test.broker.com",
            port=1883,
            username="testuser",
            password="testpass"
        )

    @patch('inputremapper.mqtt_client.mqtt')
    def test_mqtt_client_initialization(self, mock_mqtt):
        """Test MQTT client initialization."""
        # Make mqtt available by patching the check
        with patch('inputremapper.mqtt_client.MQTT_AVAILABLE', True):
            mock_mqtt.Client = Mock()

            client = MQTTClient(self.config)
            self.assertEqual(client.config, self.config)
            self.assertFalse(client.is_connected())

    def test_mqtt_client_import_error(self):
        """Test error when paho-mqtt is not available."""
        with patch('inputremapper.mqtt_client.MQTT_AVAILABLE', False):
            with self.assertRaises(ImportError) as cm:
                MQTTClient(self.config)
            self.assertIn("paho-mqtt is not installed", str(cm.exception))

    @patch('inputremapper.mqtt_client.mqtt')
    def test_publish_event_not_connected(self, mock_mqtt):
        """Test publishing when not connected attempts to connect."""
        with patch('inputremapper.mqtt_client.MQTT_AVAILABLE', True):
            mock_mqtt.Client = Mock()
            mock_client_instance = MagicMock()
            mock_mqtt.Client.return_value = mock_client_instance

            client = MQTTClient(self.config)

            # Mock the connection to fail
            with patch.object(client, 'connect', return_value=False):
                result = client.publish_event("test_device", "test_action")
                self.assertFalse(result)

    @patch('inputremapper.mqtt_client.mqtt')
    def test_test_connection(self, mock_mqtt):
        """Test the test_connection method."""
        with patch('inputremapper.mqtt_client.MQTT_AVAILABLE', True):
            mock_mqtt.Client = Mock()
            mock_client_instance = MagicMock()
            mock_mqtt.Client.return_value = mock_client_instance
            mock_mqtt.MQTT_ERR_SUCCESS = 0

            client = MQTTClient(self.config)

            # Mock successful connection and publish
            with patch.object(client, 'connect', return_value=True):
                with patch.object(client, 'publish_event', return_value=True):
                    success, message = client.test_connection()
                    self.assertTrue(success)
                    self.assertIn("Successfully connected", message)


if __name__ == "__main__":
    unittest.main()
