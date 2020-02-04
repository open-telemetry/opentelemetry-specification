# Default SDK Configuration

<details>
<summary>Table of Contents</summary>

* [Abstract](#abstract)
* [Configuration Interface](#configuration-interface)

</details>

## Abstract

The default Open Telemetry SDK (hereafter referred to as "The SDK")
is highly configurable. This specification outlines the mechanisms by
which the SDK can be configured. It does
not attempt to specify the details of what can be configured.

## Configuration Interface

### Programmatic

The SDK MUST provide a programmatic interface for all configuration.
This interface SHOULD be written in the language of the SDK itself.
All other configuration mechanisms SHOULD be built on top of this interface.

An example of this programmatic interface is accepting a well-defined
struct on an SDK builder class. From that, one could build a CLI that accepts a
file (YAML, JSON, TOML, ...) and then transforms into that well-defined struct
consumable by the programatic interface.

### Other Mechanisms

Additional configuration mechanisms SHOULD be provided in whatever
language/format/style is idiomatic for the language of the SDK. The
SDK can include as many configuration mechanisms as appropriate.
