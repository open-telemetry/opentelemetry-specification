# Glossary

This document defines some terms that are used across this specification.

Some other fundamental terms are documented in the [overview document](overview.md).

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [User Roles](#user-roles)
  * [Application Owner](#application-owner)
  * [Library Author](#library-author)
  * [Instrumentation Author](#instrumentation-author)
  * [Plugin Author](#plugin-author)
- [Common](#common)
  * [Signals](#signals)
  * [Packages](#packages)
  * [ABI Compatibility](#abi-compatibility)
  * [In-band and Out-of-band Data](#in-band-and-out-of-band-data)
  * [Manual Instrumentation](#manual-instrumentation)
  * [Automatic Instrumentation](#automatic-instrumentation)
  * [Telemetry SDK](#telemetry-sdk)
  * [Constructors](#constructors)
  * [SDK Plugins](#sdk-plugins)
  * [Exporter Library](#exporter-library)
  * [Instrumented Library](#instrumented-library)
  * [Instrumentation Library](#instrumentation-library)
  * [Instrumentation Scope](#instrumentation-scope)
  * [Tracer Name / Meter Name / Logger Name](#tracer-name--meter-name--logger-name)
  * [Execution Unit](#execution-unit)
- [Logs](#logs)
  * [Log Record](#log-record)
  * [Log](#log)
  * [Embedded Log](#embedded-log)
  * [Standalone Log](#standalone-log)
  * [Log Attributes](#log-attributes)
  * [Structured Logs](#structured-logs)
  * [Flat File Logs](#flat-file-logs)
  * [Log Appender / Bridge](#log-appender--bridge)

<!-- tocstop -->

</details>

## User Roles

### Application Owner

The maintainer of an application or service, responsible for configuring and managing the lifecycle of the OpenTelemetry SDK.

### Library Author

The maintainer of a shared library which is depended upon by many applications, and targeted by OpenTelemetry instrumentation.

### Instrumentation Author

The maintainer of OpenTelemetry instrumentation written against the OpenTelemetry API.
This may be instrumentation written within application code, within a shared library, or within an instrumentation library.

### Plugin Author

The maintainer of an OpenTelemetry SDK Plugin, written against OpenTelemetry SDK plugin interfaces.

## Common

### Signals

OpenTelemetry is structured around signals, or categories of telemetry.
Metrics, logs, traces, and baggage are examples of signals.
Each signal represents a coherent, stand-alone set of functionality.
Each signal follows a separate lifecycle, defining its current stability level.

### Packages

In this specification, the term **package** describes a set of code which represents a single dependency, which may be imported into a program independently from other packages.
This concept may map to a different term in some languages, such as "module."
Note that in some languages, the term "package" refers to a different concept.

### ABI Compatibility

An ABI (application binary interface) is an interface which defines interactions between software components at the machine code level, for example between an application executable and a compiled binary of a shared object library. ABI compatibility means that a new compiled version of a library may be correctly linked to a target executable without the need for that executable to be recompiled.

ABI compatibility is important for some languages, especially those which provide a form of machine code. For other languages, ABI compatibility may not be a relevant requirement.

### In-band and Out-of-band Data

> In telecommunications, **in-band signaling** is the sending of control information within the same band or channel used for data such as voice or video. This is in contrast to **out-of-band signaling** which is sent over a different channel, or even over a separate network ([Wikipedia](https://en.wikipedia.org/wiki/In-band_signaling)).

In OpenTelemetry we refer to **in-band data** as data that is passed
between components of a distributed system as part of business messages,
for example, when trace or baggages are included
in the HTTP requests in the form of HTTP headers.
Such data usually does not contain the telemetry,
but is used to correlate and join the telemetry produced by various components.
The telemetry itself is referred to as **out-of-band data**:
it is transmitted from applications via dedicated messages,
usually asynchronously by background routines
rather than from the critical path of the business logic.
Metrics, logs, and traces exported to telemetry backends are examples of out-of-band data.

### Manual Instrumentation

Coding against the OpenTelemetry API such as the [Tracing API](trace/api.md), [Metrics API](metrics/api.md), or others to collect telemetry from end-user code or shared frameworks (e.g. MongoDB, Redis, etc.).

### Automatic Instrumentation

Refers to telemetry collection methods that do not require the end-user to modify application's source code.
Methods vary by programming language, and examples include code manipulation (during compilation or at runtime),
monkey patching, or running eBPF programs.

Synonym: *Auto-instrumentation*.

### Telemetry SDK

Denotes the library that implements the *OpenTelemetry API*.

See [Library Guidelines](library-guidelines.md#sdk-implementation) and
[Library resource semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#telemetry-sdk).

### Constructors

Constructors are public code used by Application Owners to initialize and configure the OpenTelemetry SDK and contrib packages. Examples of constructors include configuration objects, environment variables, and builders.

### SDK Plugins

Plugins are libraries which extend the OpenTelemetry SDK. Examples of plugin interfaces are the `SpanProcessor`, `Exporter`, and `Sampler` interfaces.

### Exporter Library

Exporters are SDK Plugins which implement the `Exporter` interface, and emit telemetry to consumers.

### Instrumented Library

Denotes the library for which the telemetry signals (traces, metrics, logs) are gathered.

The calls to the OpenTelemetry API can be done either by the Instrumented Library itself,
or by another [Instrumentation Library](#instrumentation-library).

Example: `org.mongodb.client`.

### Instrumentation Library

Denotes the library that provides the instrumentation for a given [Instrumented Library](#instrumented-library).
*Instrumented Library* and *Instrumentation Library* may be the same library
if it has built-in OpenTelemetry instrumentation.

See [Overview](overview.md#instrumentation-libraries) for a more detailed definition and naming guidelines.

Example: `io.opentelemetry.contrib.mongodb`.

Synonyms: *Instrumenting Library*.

### Instrumentation Scope

A logical unit of the application code with which the emitted telemetry can be
associated. It is typically the developer's choice to decide what denotes a
reasonable instrumentation scope. The most common approach is to use the
[instrumentation library](#instrumentation-library) as the scope, however other
scopes are also common, e.g. a module, a package, or a class can be chosen as
the instrumentation scope.

If the unit of code has a version then the instrumentation scope is defined by
the (name,version) pair otherwise the version is omitted and only the name is
used. The name or (name,version) pair uniquely identify the logical unit of the
code that emits the telemetry. A typical approach to ensure uniqueness is to use
fully qualified name of the emitting code (e.g. fully qualified library name or
fully qualified class name).

The instrumentation scope is used to obtain a
[Tracer, Meter, or Logger](#tracer-name--meter-name--logger-name).

The instrumentation scope may have zero or more additional attributes that provide
additional information about the scope. For example for a scope that specifies an
instrumentation library an additional attribute may be recorded to denote the URL of the
repository URL the library's source code is stored. Since the scope is a build-time
concept the attributes of the scope cannot change at runtime.

### Tracer Name / Meter Name / Logger Name

This refers to the `name` and (optional) `version` arguments specified when
creating a new `Tracer` or `Meter` (see
[Obtaining a Tracer](trace/api.md#tracerprovider)/[Obtaining a Meter](metrics/api.md#meterprovider))/[Obtaining a Logger](logs/bridge-api.md#loggerprovider).
The name/version pair identifies the
[Instrumentation Scope](#instrumentation-scope), for example the
[Instrumentation Library](#instrumentation-library) or another unit of
application in the scope of which the telemetry is emitted.

### Execution Unit

An umbrella term for the smallest unit of sequential code execution, used in different concepts of multitasking. Examples are threads, coroutines or fibers.

## Logs

### Log Record

A recording of an event. Typically the record includes a timestamp indicating
when the event happened as well as other data that describes what happened,
where it happened, etc.

Synonyms: *Log Entry*.

### Log

Sometimes used to refer to a collection of Log Records. May be ambiguous, since
people also sometimes use `Log` to refer to a single `Log Record`, thus this
term should be used carefully and in the context where ambiguity is possible
additional qualifiers should be used (e.g. `Log Record`).

### Embedded Log

`Log Records` embedded inside a [Span](trace/api.md#span)
object, in the [Events](trace/api.md#add-events) list.

### Standalone Log

`Log Records` that are not embedded inside a `Span` and are recorded elsewhere.

### Log Attributes

Key/value pairs contained in a `Log Record`.

### Structured Logs

Logs that are recorded in a format which has a well-defined structure that allows
to differentiate between different elements of a Log Record (e.g. the Timestamp,
the Attributes, etc). The *Syslog protocol* ([RFC 5424](https://tools.ietf.org/html/rfc5424)),
for example, defines a `structured-data` format.

### Flat File Logs

Logs recorded in text files, often one line per log record (although multiline
records are possible too). There is no common industry agreement whether
logs written to text files in more structured formats (e.g. JSON files)
are considered Flat File Logs or not. Where such distinction is important it is
recommended to call it out specifically.

### Log Appender / Bridge

A log appender or bridge is a component which bridges logs from an existing log
API into OpenTelemetry using the [Log Bridge API](./logs/bridge-api.md). The
terms "log bridge" and "log appender" are used interchangeably, reflecting that
these components bridge data into OpenTelemetry, but are often called appenders
in the logging domain.
