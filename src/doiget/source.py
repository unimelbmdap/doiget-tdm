
import dataclasses
import typing

import upath


SourceLink: typing.TypeAlias = upath.UPath | typing.Sequence[upath.UPath]


@dataclasses.dataclass
class Source:
    acq_method: typing.Callable[[SourceLink], bytes]
    link: SourceLink
