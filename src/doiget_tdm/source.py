from __future__ import annotations

import dataclasses
import typing

import upath

import doiget_tdm.format
import doiget_tdm.validate


SourceLink: typing.TypeAlias = upath.UPath | typing.Sequence[upath.UPath]


@dataclasses.dataclass
class Source:
    """
    A full-text data source.

    Parameters
    ----------
    acq_func
        Function that can be used to acquire the source data.
    link
        Location of the source data.
    format_name
        The format of the source data.
    encrypt
        Whether to encrypt the data after acquisition.
    validator_func
        Function that validates data acquired for the source.

    """

    acq_func: typing.Callable[[Source], bytes]
    link: SourceLink
    format_name: doiget_tdm.format.FormatName
    encrypt: bool = False
    validator_func: typing.Callable[[bytes, doiget_tdm.format.FormatName], bool] = (
        doiget_tdm.validate.validate_data
    )

    def acquire(self) -> bytes:
        """
        Attempt to acquire the full-text content from the source.
        """
        return self.acq_func(self)

    def validate(self, data: bytes) -> bool:
        """
        Validate the full-text data.

        Parameters
        ----------
        data
            Raw data.

        Returns
        -------
            Whether the data was deemed as valid.
        """
        return self.validator_func(data, self.format_name)
