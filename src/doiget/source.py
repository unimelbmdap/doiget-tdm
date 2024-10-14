from __future__ import annotations

import dataclasses
import typing

import upath

import doiget.format


SourceLink: typing.TypeAlias = upath.UPath | typing.Sequence[upath.UPath]


@dataclasses.dataclass
class Source:
    acq_method: typing.Callable[[SourceLink], bytes]
    link: SourceLink
    format_name: doiget.format.FormatName
    encrypt: bool = False
