# Barely JSON

[![GitHub Actions badge](https://github.com/torfsen/barely_json/actions/workflows/test.yml/badge.svg)](https://github.com/torfsen/barely_json/actions/workflows/test.yml)

*A Python package for parsing data that only looks like JSON*

    from barely_json import parse
    print(parse('[what is this?, , {perhaps, json: no}]'))

    # Prints ['what is this?', '', {'perhaps': '', 'json': False}]

Quite a bit of data looks like JSON at a first glance but turns out not to comply completely with the JSON specification -- often because the exporting software is broken, but sometimes simply because the format was never intended to be JSON in the first place.

No matter how you ended up with the data, now you want to parse it! However, most JSON parsers are pretty strict, so you're out of luck with your JSON-esque mess.

That's where *Barely JSON* steps in and tries to parse anything that remotely looks like JSON. In addition to the pure parsing, *Barely JSON* will also try to post-process your data into suitable Python types even if your data provider uses, for example, `on` and `off` as boolean literals.


# Installation

The supported Python versions are 3.7 and later.

    pip install barely_json


# Usage

The main routine is `parse`:

    > from barely_json import parse
    > parse("[NaN, , {state: off, where's my value?}, NULL]")

    [nan, '', {'state': False, "where's my value?": ''}, None]

As you can see, `parse` by default tries to convert values that are illegal in JSON into hopefully appropriate Python types, which often works well. But sometimes that's not what you want, so you can disable the auto-conversion:

    > parse("[NaN, , {state: off, where's my value?}, NULL]", resolver=None)

    [<IllegalValue 'NaN'>,
     <IllegalValue ''>,
     {<IllegalValue 'state'>: <IllegalValue 'off'>,
      <IllegalValue "where's my value?">: <IllegalValue ''>},
     <IllegalValue 'NULL'>]

In that case any value that's illegal or missing is wrapped in an instance of a special `IllegalValue` class. You can also provide your own resolver for illegal values, which is simply a callback that maps strings to arbitrary values:

    > from barely_json import default_resolver
    >
    > def my_resolver(text):
    >     if text.lower() == 'one':
    >         return 1
    >     return default_resolver(text)
    >
    > parse('[one, FALSE]', resolver=my_resolver)

    [1, False]

When writing your own resolver it's often handy to fall back to`default_resolver` after you've handled your special cases.


# Change Log

See `CHANGELOG.md`.


# License

Distributed under the MIT license. See the file `LICENSE` for details.


# Contributors

* [@torfsen](https://github.com/torfsen)
* [@tusharmakkar08](https://github.com/tusharmakkar08)
* [@gvx](https://github.com/gvx)


# Development

Clone the repository:

    git clone https://github.com/torfsen/barely_json.git
    cd barely_json

Install the development dependencies

    pip install -r requirements-dev.txt

Run the tests:

    tox

For pull requests, the tests are run using GitHub actions.


[virtualenv]: https://virtualenv.pypa.io
[tox]: https://tox.readthedocs.io
