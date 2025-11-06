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

"""Starts injecting keycodes based on the configuration."""

import sys
import multiprocessing
from argparse import ArgumentParser

from inputremapper.configs.global_config import GlobalConfig
from inputremapper.injection.global_uinputs import GlobalUInputs, UInput
from inputremapper.injection.mapping_handlers.mapping_parser import MappingParser
from inputremapper.logging.logger import logger
from inputremapper.mqtt_client import initialize_mqtt_client, shutdown_mqtt_client


class InputRemapperServiceBin:
    @staticmethod
    def main() -> None:
        parser = ArgumentParser()
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            dest="debug",
            help="Displays additional debug information",
            default=False,
        )
        parser.add_argument(
            "--hide-info",
            action="store_true",
            dest="hide_info",
            help="Don't display version information",
            default=False,
        )

        options = parser.parse_args(sys.argv[1:])

        # Python 3.14 compatibility
        multiprocessing.set_start_method("fork")

        logger.update_verbosity(options.debug)

        # import input-remapper stuff after setting the log verbosity
        from inputremapper.daemon import Daemon

        if not options.hide_info:
            logger.log_info("input-remapper-service")

        # Initialize MQTT client for Home Assistant integration
        logger.info("Initializing MQTT client for Home Assistant...")
        try:
            if initialize_mqtt_client():
                logger.info("MQTT client initialized successfully")
            else:
                logger.warning(
                    "Failed to initialize MQTT client. "
                    "The service will continue but MQTT publishing will not work. "
                    "Please create ~/mqtt_config.json with your MQTT broker settings."
                )
        except Exception as e:
            logger.error(f"Exception during MQTT client initialization: {e}")
            logger.warning("Service will continue without MQTT functionality")
            import traceback
            logger.debug(f"MQTT init traceback:\n{traceback.format_exc()}")

        try:
            logger.info("Creating daemon components...")
            global_config = GlobalConfig()
            global_uinputs = GlobalUInputs(UInput)
            mapping_parser = MappingParser(global_uinputs)

            logger.info("Initializing daemon...")
            daemon = Daemon(global_config, global_uinputs, mapping_parser)

            logger.info("Publishing D-Bus service...")
            daemon.publish()

            logger.info("Starting daemon main loop...")
            daemon.run()
        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Fatal error in service: {e}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            sys.exit(1)
        finally:
            # Cleanup
            logger.info("Shutting down MQTT client...")
            try:
                shutdown_mqtt_client()
            except Exception as e:
                logger.error(f"Error during MQTT shutdown: {e}")
