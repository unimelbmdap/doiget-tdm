# doiget-tdm

`doiget-tdm` is a command-line application and Python library for obtaining the metadata and full-text of published journal articles.
It is primarily intended for use in text data mining projects where the user has subscriptions to full-text content and data exchange agreements where necessary.

> [!WARNING]
> This package is still in development and should be considered as alpha quality.

## Features

* Acquire full-text of published articles, with built-in support for multiple publishers and their acquisition methods (e.g., network or local files).
* Customise acquisition and add additional publishers.
* Retrieve article metadata from [Crossref](https://crossref.org).


## Installation

The package can be installed using `pip`:

```bash
pip install git+https://github.com/unimelbmdap/doiget-tdm
```

## Quickstart

Show the default configuration settings:

```bash
doiget-tdm show-config
```

Download the full-text (XML) of the journal article with DOI [`10.1371/journal.pbio.1002611`](https://doi.org/10.1371/journal.pbio.1002611) to the default directory:

```bash
doiget-tdm acquire '10.1371/journal.pbio.1002611'
```

## Documentation

See the [documentation](https://unimelbmdap.github.io/doiget-tdm/) for detailed information about how to use `doiget-tdm`.
