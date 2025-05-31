from __future__ import annotations

# class TagStripper(HTMLParser):
#     def __init__(self) -> None:
#         super().__init__(convert_charrefs=False)
#
#         self.reset()
#         self.fed: list[str] = []
#
#     def handle_data(self, d: str) -> None:
#         self.fed.append(d)
#
#     def handle_entityref(self, name: str) -> None:
#         self.fed.append(f"&{name};")
#
#     def handle_charref(self, name: str) -> None:
#         self.fed.append(f"&#{name};")
#
#     def get_data(self) -> str:
#         return "".join(self.fed)
#
#
# def _strip(value: str) -> str:
#     s = TagStripper()
#     s.feed(value)
#     s.close()
#
#     return s.get_data()
#
#
# def strip_tags(value: str) -> str:
#     while "[" in value and "]" in value:
#         new_value = _strip(value)
#         if value.count("[") == new_value.count("]"):
#             break
#
#         value = new_value
#
#     return value





