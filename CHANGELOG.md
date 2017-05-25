# Change Log for Barely JSON

The format of this file is based on [Keep a Changelog] and this project adheres to [Semantic Versioning].


## [Unreleased]

### Fixed

- `IllegalValue.__str__` was broken (reported and fixed by [@tusharmakkar08] in [#4])

### Changed

- Code cleanup (contributed by [@gvx] in [#3])


## [0.1.1] (2017-05-12)

### Fixed

- Floats were not parsed correctly ([#1])
- String escapes were not parsed correctly ([#2])


## 0.1.0 (2017-05-12)

### Added

- Support for parsing strings
- Support for custom resolvers for illegal values


[Keep a Changelog]: http://keepachangelog.com/
[Semantic Versioning]: http://semver.org/

[Unreleased]: https://github.com/torfsen/barely_json/compare/v0.1.1...master
[0.1.1]: https://github.com/torfsen/barely_json/compare/v0.1.0...v0.1.1

[@gvx]: https://github.com/gvx
[@tusharmakkar08]: https://github.com/tusharmakkar08

[#1]: https://github.com/torfsen/barely_json/issues/1
[#2]: https://github.com/torfsen/barely_json/issues/2
[#3]: https://github.com/torfsen/barely_json/pull/3
[#4]: https://github.com/torfsen/barely_json/pull/4

