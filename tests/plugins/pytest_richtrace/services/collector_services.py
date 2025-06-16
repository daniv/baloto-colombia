# Project : baloto-colombia
# File Name : dependencies.py
# Dir Path : tests/plugins/pytest_richtrace/services
# Created on: 2025–06–15 at 00:52:14.
# Package :

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pathlib import Path

from requests.packages import package

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any
    from pluggy._manager import DistFacade


class PythonCollectorService:
    name = "python-collector-service"

    @pytest.hookimpl(tryfirst=True)
    def pytest_collect_env_info(self, config: pytest.Config) -> dict[str, Any]:
        """Collect version information about the python and visrtual ebvironment used

        :param config: The pytest config
        :return: a dictionaru with collected information
        """
        import sys
        import platform

        # -- adding pypy_version_info idf available
        pypy_version_info = getattr(sys, "pypy_version_info", None)
        if pypy_version_info:
            verinfo = ".".join(map(str, pypy_version_info[:3]))
            pypy_kv = f"{verinfo} - {pypy_version_info[3]}"

        # -- adding python executable path
        executable_kv = Path(sys.executable).relative_to(config.rootpath).as_posix()

        return dict(
            platform=f"{sys.platform} - {platform.platform()}",
            python=platform.python_version(),
            python_ver_info=".".join(map(str, sys.version_info)),
            pypy=locals().get("pypy_kv", None),
            executable=Path(sys.executable).relative_to(config.rootpath).as_posix(),
        )


class PytestCollectorService:
    name = "pytest-collector-service"

    @pytest.hookimpl(tryfirst=True)
    def pytest_collect_env_info(self, config: pytest.Config) -> dict[str, Any]:
        """Collect information about pytest

        :param config: The pytest config
        :return: a dictionary with the collected information.
        """
        import shlex

        return dict(
            pytest_ver=pytest.__version__,
            invocation_params=shlex.join(config.invocation_params.args),
        )


class PoetryCollectorService:
    name = "poetry-collector-service"

    @pytest.hookimpl(trylast=True)
    def pytest_collect_env_info(self) -> dict[str, Any]:
        """Collects informatio about poetry

        :return: a dictionary of the collected data
        """
        import re
        import shlex
        import subprocess
        import warnings
        from baloto.__version__ import __version__

        try:
            show = subprocess.Popen(
                shlex.split("poetry show -l -T"), stdout=subprocess.PIPE, text=True
            )
            output, error = show.communicate()
            show.stdout.close()
            if output:
                packages = self.generate_output(output.splitlines())
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            if error.output:
                packages = self.generate_output(error.output.splitlines())
            else:
                msg = f"Unable to get required pacages info.\nreason = {str(error)}"
                warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
        else:
            result_ver = subprocess.run(
                shlex.split("poetry -V"),
                capture_output=True,
                text=True,
                encoding="utf-8",
                shell=True,
            )
            return dict(
                poetry_version=re.findall("[0-9.]+", result_ver.stdout.strip())[0],
                project_version=__version__,
                packages=locals().get("packages", None),
            )

    @staticmethod
    def generate_output(lines: list[str]):
        import semver
        from importlib.metadata import metadata

        packages = []
        packs = tuple(map(lambda x: tuple(filter(len, x.split(" ")))[:3], lines))
        for name, currentv, latestv in packs:
            comp = semver.Version.parse(str(currentv)).compare(str(latestv))
            latestv = f"[bright_red]{latestv}[/]" if comp < 0 else f"[bright_green]{latestv}[/]"
            pack = dict(
                name=name,
                current_ver=currentv,
                latest_ver=latestv,
                summary=metadata(str(name)).json["summary"],
            )
            packages.append(pack)
        return packages


class PluggyCollectorService:
    name = "pluggy-collector-service"

    def __init__(self) -> None:
        self.config: pytest.Config | None = None
        self.pluginmanager: pytest.PytestPluginManager | None = None

    @pytest.hookimpl
    def pytest_collect_env_info(self, config: pytest.Config) -> dict[str, Any]:
        """
        Following pytest rules on displaying plugins on headers:
            - --debug not set and --trace-config not set -> registered
            - --debug not set and --trace-config was set -> registered + active
            - --debug was set and --trace-config was not set -> registered
            - --debug was set and also --trace-config was set -> registered + active

        :param config: the pytest.Config instance
        :return: a dictionary with pluggy info
        """
        import pluggy

        pluginmanager = config.pluginmanager
        self.pluginmanager = pluginmanager
        self.config = config

        dist_info = self._plugin_distinfo()
        names_info = self._name_plugin()
        return dict(
            plugins=dict(
                pluggy_version=pluggy.__version__,
                dist_title="registered third-party plugins",
                name_title="active plugins",
                dist_info=dist_info if dist_info else None,
                names_info=names_info if names_info else None,
            )
        )

    def _iter_distinfo(self) -> Iterator[tuple[object, DistFacade]]:
        for dist_info in iter(self.pluginmanager.list_plugin_distinfo()):
            yield dist_info

    def _iter_name_plugin(self) -> Iterator[str, str]:
        for plugin in iter(self.pluginmanager.list_name_plugin()):
            if str(repr(plugin[1])).find("collector_services") > 0:
                continue
            yield plugin

    def _plugin_distinfo(self) -> list[dict[str, str]]:
        from glom import glom

        assert self.config is not None
        assert self.pluginmanager is not None

        dists: list[dict[str, str]] = []

        for plugin, facade in self._iter_distinfo():
            location = getattr(plugin, "__file__", repr(plugin))
            if Path(location).is_file():
                location = Path(location).relative_to(self.config.rootpath).as_posix()
            dists.append(
                dict(
                    name=facade.name,
                    version=facade.version,
                    project_name=facade.project_name,
                    summary=glom(facade, "metadata.json.summary", default=""),
                    plugin=location,
                )
            )
        return dists

    def _name_plugin(self) -> list[dict[str, str]]:
        assert self.config is not None
        assert self.pluginmanager is not None

        names: list[dict[str, str]] = []
        for name, plugin in self._iter_name_plugin():
            if plugin is None:
                continue
            if len(name) > 25:
                if Path(name).is_file():
                    p = Path(name)
                    name = f"{p.parent.name}/{p.name}"
            location = getattr(plugin, "__file__", repr(plugin))
            if Path(location).is_file():
                try:
                    location = Path(location).relative_to(self.config.rootpath).as_posix()
                except ValueError as e:
                    location = Path(location).relative_to(Path.home()).as_posix()
                    names.append(dict(name=name, plugin=location))
            else:
                names.append(dict(name=name, plugin=location))


        return names


class HookHeaderCollectorService:
    name = "hook-header-collector-service"

    @pytest.hookimpl(trylast=True)
    def pytest_collect_env_info(self, config) -> dict[str, Any]:
        """Coolec information from pytest hook pytest_report_header

        :param config: The pytest.Config instance
        :return: a dictionary with collected infoemation
        """
        data = {}
        lines = config.hook.pytest_report_header(
            config=config, start_path=config.invocation_params.dir
        )
        for line_or_lines in lines:
            if not line_or_lines: continue
            if isinstance(line_or_lines, str):
                line_or_lines = [line_or_lines]
            if bool(line_or_lines[0].find("using") >= 0):
                continue
            for line in line_or_lines:
                partition = list(map(str.strip, line.partition(": ")))
                if len(partition) > 3:
                    continue
                # TODO: view thos article about match case
                match partition[0]:
                    case "rootdir":
                        data["rootdir"] = Path(partition[2]).as_posix()
                    case "plugins":
                        pass
                    case _:
                        data[partition[0]] = partition[2]
        return data


class CollectorWrapper:
    name = "collector-wrapper"

    @pytest.hookimpl(wrapper=True)
    def pytest_collect_env_info(self) -> dict[str, None]:
        """Wraps other hook calls and resule the return values

        :return: a single map that was chained from hook responses
        """
        from collections import ChainMap

        outcomes = yield

        maps = []
        for outcome in outcomes:
            child = dict(filter(lambda x: x[1] is not None and x[1] != "", outcome.items()))
            maps.append(child)

        return ChainMap(*maps)
