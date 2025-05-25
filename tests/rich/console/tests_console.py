from __future__ import annotations

import collections
import colorsys
import io
from time import process_time
from typing import Generator
from collections.abc import Callable

import pytest
from rich import box
from rich.color import Color
from rich.console import Console, ConsoleOptions, Group, RenderableType, RenderResult
from rich.markdown import Markdown
from rich.measure import Measurement
from rich.pretty import Pretty
from rich.segment import Segment
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.columns import Columns




@pytest.mark.parametrize(
    "feature, title", [
        ("color_table", "Colors"),
        ("styles_table", "Style")
    ],
    ids=["color", "styles"]
)
def rich_card_test(
    feature: str,
    title: str,
    test_card: Table,
    create_table: Callable[[str], Table]
):
    console = Console()

    console.line()
    console.rule(feature, characters="=", style="green bold dim")
    console.line()

    table = create_table(feature)
    # console.print(table)
    start = process_time()
    test_card.add_row(title, table)
    console.print(test_card)
    taken = round((process_time() - start) * 1000.0, 1)
    print(f"rendered in {taken}ms ({feature})")
    console.line()


@pytest.fixture(scope="function")
def test_card() -> Table:
    table = Table.grid(padding=1, pad_edge=True)
    table.title = "Rich features"
    table.add_column("Feature", no_wrap=True, justify="center", style="bold red")
    table.add_column("Demonstration")
    return table

@pytest.fixture
def create_table() -> Generator[Callable[[str], Table], Table, None]:
    def _create_table(feature: str):
        match feature:
            case "color_table":
                return make_color_table()
            case "styles_table":
                return make_styles_table()
            case _:
                raise KeyError(f"The feure fucntion '{feature}' does not match any defined callabe")


    yield _create_table

def feature_table() -> Table:
    return  Table(
        box=None,
        expand=False,
        show_header=False,
        show_edge=False,
        pad_edge=False,
    )

def make_color_table() -> Table:

    class ColorBox:
        def __rich_console__(
                self, console: Console, options: ConsoleOptions
        ) -> RenderResult:
            for y in range(0, 5):
                for x in range(options.max_width):
                    h = x / options.max_width
                    l = 0.1 + ((y / 5) * 0.7)
                    r1, g1, b1 = colorsys.hls_to_rgb(h, l, 1.0)
                    r2, g2, b2 = colorsys.hls_to_rgb(h, l + 0.7 / 10, 1.0)
                    bgcolor = Color.from_rgb(r1 * 255, g1 * 255, b1 * 255)
                    color = Color.from_rgb(r2 * 255, g2 * 255, b2 * 255)
                    yield Segment("▄", Style(color=color, bgcolor=bgcolor))
                yield Segment.line()

        def __rich_measure__(
                self, console: "Console", options: ConsoleOptions
        ) -> Measurement:
            return Measurement(1, options.max_width)

    t = feature_table()
    t.add_row(
        (
            "✓ [bold green]4-bit color[/]\n"
            "✓ [bold blue]8-bit color[/]\n"
            "✓ [bold magenta]Truecolor (16.7 million)[/]\n"
            "✓ [bold yellow]Dumb terminals[/]\n"
            "✓ [bold cyan]Automatic color conversion"
        ),
        ColorBox(),
    )

    return t


def make_styles_table() -> Table:
    styles_dict = Style.STYLE_ATTRIBUTES.copy()
    styles_dict.update(
        {
            "link": Style(color=None, link="https://www.textualize.io/"),
            # "meta": Style(color=None, meta=True),
        }
    )

    columns = Columns(
        list(map(lambda x: f"{x}: [{x}]{x}[/]", list(sorted(Style.STYLE_ATTRIBUTES.keys())))),
        align="left",
    )
    t = feature_table()
    t.add_row("Style", columns)

    return t
