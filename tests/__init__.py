from __future__ import annotations

import inspect
import logging
import allure_commons
from pytest import UsageError
from typing import Callable
from typing import Any
from types import FrameType


class AllureStepLogger:
    def __init__(self, config):
        # Create a logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Get --allure-step-log-level value
        self.level = config.option.allure_step_log_level
        if isinstance(self.level, str):
            self.level = self.level.upper()

        try:
            self.level = int(getattr(logging, self.level, self.level))
        except ValueError as e:
            # Python logging does not recognise this as a logging level
            raise UsageError(
                "'{}' is not recognized as a logging level name for "
                "'{}'. Please consider passing the "
                "logging level num instead.".format(self.level, self.__class__.__name__)
            ) from e

    @allure_commons.hookimpl
    def start_step(self, uuid: str, title: str, params: dict[str, str]):
        """Add a hook implementation to log every step"""
        # get test_* function name from stack
        filename, func_name, line_no, locals_ = self._caller_frame_info(10)
        # log a message using defined logger and log level
        self.logger.log(self.level, f"{func_name}: {title}")

    @staticmethod
    def _caller_frame_info(
            offset: int,
            currentframe: Callable[[], FrameType | None] = inspect.currentframe,
    ) -> tuple[str, str, int, dict[str, Any]]:
        not_found = True
        offset += 1

        frame = currentframe()
        if frame is not None:
            while offset and not_found and frame is not None:
                frame = frame.f_back
                offset -= 1
                not_found = not frame.f_code.co_name.endswith("_test")
            assert frame is not None
            return frame.f_code.co_filename,frame.f_code.co_name, frame.f_lineno, frame.f_locals
        else:
            return "filename", "function", 0, {}
