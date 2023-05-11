# General attributes

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**Status**: [Experimental](../../document-status.md)

The attributes described in this section are not specific to a particular operation but rather generic.
They may be used in any Span they apply to.
Particular operations may refer to or require some of these attributes.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Server and client attributes](#server-and-client-attributes)
  * [Server attributes](#server-attributes)
    + [`server.address`](#serveraddress)
    + [`server.socket.*` attributes](#serversocket-attributes)
  * [Client attributes](#client-attributes)
    + [Connecting through intermediary](#connecting-through-intermediary)
- [Network attributes](#network-attributes)
  * [Source and destination attributes](#source-and-destination-attributes)
    + [Source](#source)
    + [Destination](#destination)
  * [Network connection and carrier attributes](#network-connection-and-carrier-attributes)
- [General remote service attributes](#general-remote-service-attributes)
- [General identity attributes](#general-identity-attributes)
- [General thread attributes](#general-thread-attributes)
- [Source Code Attributes](#source-code-attributes)

<!-- tocstop -->

## Server and client attributes

These attributes may be used to describe the client and server in a connection-based network interaction
where there is one side that initiates the connection (the client is the side that initiates the connection).
This covers all TCP network interactions since TCP is connection-based and one side initiates the
connection (an exception is made for peer-to-peer communication over TCP where the "user-facing" surface of the
protocol / API does not expose a clear notion of client and server).
This also covers UDP network interactions where one side initiates the interaction, e.g. QUIC (HTTP/3) and DNS.

In an ideal situation, not accounting for proxies, multiple IP addresses or host names,
the `server.*` attributes are the same on the client and server.

### Server attributes

> **Warning**
> Attributes in this section are in use by the HTTP semantic conventions.
Once the HTTP semantic conventions are declared stable, changes to the attributes in this section will only be allowed
if they do not cause breaking changes to HTTP semantic conventions.

<!-- semconv server -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `server.address` | string | Logical server hostname, matches server FQDN if available, and IP or socket address if FQDN is not known. | `example.com` | Recommended |
| `server.port` | int | Logical server port number | `80`; `8080`; `443` | Recommended |
| `server.socket.domain` | string | The domain name of an immediate peer. [1] | `proxy.example.com` | Recommended |
| `server.socket.address` | string | Physical server IP address or Unix socket address. | `10.5.3.2` | Recommended: If different than `server.address`. |
| `server.socket.port` | int | Physical server port. | `16456` | Recommended: If different than `server.port`. |

**[1]:** Typically observed from the client side, and represents a proxy or other intermediary domain name.
<!-- endsemconv -->

`server.address` and `server.port` represent logical server name and port. Semantic conventions that refer to these attributes SHOULD
specify what these attributes mean in their context.

Semantic conventions and instrumentations that populate both logical (`server.address` and `server.port`) and socket-level (`server.socket.*`) attributes SHOULD set socket-level attributes only when they don't match logical ones. For example, when direct connection to the remote destination is established and `server.address` is populated, `server.socket.domain` SHOULD NOT be set. Check out [Connecting through intermediary](#connecting-through-intermediary) for more information.

#### `server.address`

For IP-based communication, the name should be a DNS host name of the service. On client side it matches remote service name, on server side, it represents local service name as seen externally on clients.

When connecting to an URL `https://example.com/foo`, `server.address` matches `"example.com"` on both client and server side.

On client side, it's usually passed in form of URL, connection string, host name, etc. Sometimes host name is only available to instrumentation as a string which may contain DNS name or IP address. `server.address` SHOULD be set to the available known hostname (e.g., `"127.0.0.1"` if connecting to an URL `https://127.0.0.1/foo`).

If only IP address is available, it should be populated on `server.address`. Reverse DNS lookup SHOULD NOT be used to obtain DNS name.

If `network.transport` is `"pipe"`, the absolute path to the file representing it should be used as `server.address`.
If there is no such file (e.g., anonymous pipe),
the name should explicitly be set to the empty string to distinguish it from the case where the name is just unknown or not covered by the instrumentation.

For Unix domain socket, `server.address` attribute represents remote endpoint address on the client side and local endpoint address on the server side.

#### `server.socket.*` attributes

_Note: this section applies to socket connections visible to instrumentations. Instrumentations have limited knowledge about intermediaries communications goes through such as [transparent proxies](https://www.rfc-editor.org/rfc/rfc3040.html#section-2.5) or VPN servers. Higher-level instrumentations such as HTTP don't always have access to the socket-level information and may not be able to populate socket-level attributes._

Socket-level attributes identify peer and host that are directly connected to each other. Since instrumentations may have limited knowledge on network information, instrumentations SHOULD populate such attributes to the best of their knowledge when populate them at all.

_Note: Specific structures and methods to obtain socket-level attributes are mentioned here only as examples. Instrumentations would usually use Socket API provided by their environment or sockets implementations._

For IP-based communication, `server.socket.domain` represents either fully qualified domain name of immediate peer and `server.socket.address` to the IP address (or one specific to network family).

`server.socket.domain`, `server.socket.address`, and `server.socket.port` describe server side of socket communication. For example, when connecting using `connect(2)`
on [Linux](https://man7.org/linux/man-pages/man2/connect.2.html) or [Windows](https://docs.microsoft.com/windows/win32/api/winsock2/nf-winsock2-connect)
with `AF_INET` address family, they represent `sin_addr` and `sin_port` fields of [`sockaddr_in`](https://man7.org/linux/man-pages/man7/ip.7.html) structure.

On client side, address and port can be obtained by calling `getpeername` method on [Linux](https://man7.org/linux/man-pages/man2/getpeername.2.html) or
[Windows](https://docs.microsoft.com/windows/win32/api/winsock2/nf-winsock2-getpeername).

On server side address and port can be obtained by calling `getsockname` method on [Linux](https://man7.org/linux/man-pages/man2/getsockname.2.html) or
[Windows](https://docs.microsoft.com/windows/win32/api/winsock2/nf-winsock2-getsockname).

`server.socket.port` SHOULD only be populated for families that have notion of port.

### Client attributes

> **Warning**
> Attributes in this section are in use by the HTTP semantic conventions.
Once the HTTP semantic conventions are declared stable, changes to the attributes in this section will only be allowed
if they do not cause breaking changes to HTTP semantic conventions.

<!-- semconv client -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `client.address` | string | Client address - unix domain socket name, IPv4 or IPv6 address. [1] | `/tmp/my.sock`; `10.1.2.80` | Recommended |
| `client.port` | int | Client port number [2] | `65123` | Recommended |
| `client.socket.address` | string | Immediate client peer address - unix domain socket name, IPv4 or IPv6 address. | `/tmp/my.sock`; `127.0.0.1` | Recommended: If different than `client.address`. |
| `client.socket.port` | int | Immediate client peer port number | `35555` | Recommended: If different than `client.port`. |

**[1]:** When observed from the server side, and when communicating through an intermediary, `client.address` SHOULD represent client address behind any intermediaries (e.g. proxies) if it's available.

**[2]:** When observed from the server side, and when communicating through an intermediary, `client.port` SHOULD represent client port behind any intermediaries (e.g. proxies) if it's available.
<!-- endsemconv -->

`client.socket.address` and `client.socket.port` represent physical client name and port.

For IP-based communication, the `client.socket.address` should be a IP address, Unix domain name, or another address specific to network type.

On server side, `client.socket.address` identifies the direct peer endpoint socket address. For example, when using `bind(2)`
on [Linux](https://man7.org/linux/man-pages/man2/bind.2.html) or [Windows](https://docs.microsoft.com/windows/win32/api/winsock2/nf-winsock2-bind)
with `AF_INET` address family, represent `sin_addr` and `sin_port` fields of `sockaddr_in` structure.

On client side it represents local socket address and port can be obtained by calling `getsockname` method on [Linux](https://man7.org/linux/man-pages/man2/getsockname.2.html),
[Windows](https://docs.microsoft.com/windows/win32/api/winsock2/nf-winsock2-getsockname).

#### Connecting through intermediary

When connecting to the remote destination through an intermediary (e.g. proxy), client instrumentations SHOULD set `server.address` and `server.port` to logical remote destination address and `server.socket.name`, `server.socket.address` and `server.socket.port` to the socket peer connection is established with - the intermediary.

`server.socket.domain` SHOULD be set to the DNS name used to resolve `server.socket.address` if it's readily available. Instrumentations
SHOULD NOT do DNS lookups to obtain `server.socket.address`. If peer information available to instrumentation
can represent DNS name or IP address, instrumentation SHOULD NOT attempt to parse it and SHOULD only set `server.socket.domain`.

_Note: Telemetry consumers can obtain IP address from telemetry item by first checking `server.socket.address` and if not present, falling back to `server.socket.domain`._

For example, [URL Host component](https://www.rfc-editor.org/rfc/rfc3986#section-3.2.2) can contain IP address or DNS name and
instrumentations that don't have access to socket-level communication can only populate `server.socket.domain`.
Instrumentations that have access to socket connection, may be able to populate valid `server.socket.address` instead of or
in addition to DNS name.

Server instrumentations that leverage `client.address` and `client.port` attributes SHOULD set them to originating client address and port behind all proxies if this information is available.
The `client.socket.address` and `client.socket.port` attributes then SHOULD contain immediate client peer address and port.

If only immediate peer information is available, it should be set on `client.address` and `client.port` and `client.socket.*` attributes SHOULD NOT be set.

## Network attributes

> **Warning**
> Attributes in this section are in use by the HTTP semantic conventions.
Once the HTTP semantic conventions are declared stable, changes to the attributes in this section will only be allowed
if they do not cause breaking changes to HTTP semantic conventions.

<!-- semconv network-core -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `network.transport` | string | [OSI Transport Layer](https://osi-model.com/transport-layer/) or [Inter-process Communication method](https://en.wikipedia.org/wiki/Inter-process_communication). The value SHOULD be normalized to lowercase. | `tcp`; `udp` | Recommended |
| `network.type` | string | [OSI Network Layer](https://osi-model.com/network-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `ipv4`; `ipv6` | Recommended |
| `network.protocol.name` | string | [OSI Application Layer](https://osi-model.com/application-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `amqp`; `http`; `mqtt` | Recommended |
| `network.protocol.version` | string | Version of the application layer protocol used. See note below. [1] | `3.1.1` | Recommended |

**[1]:** `network.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

`network.transport` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `tcp` | TCP |
| `udp` | UDP |
| `pipe` | Named or anonymous pipe. See note below. |
| `unix` | Unix domain socket |

`network.type` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `ipv4` | IPv4 |
| `ipv6` | IPv6 |
<!-- endsemconv -->

### Source and destination attributes

These attributes may be used to describe the sender and receiver of a network exchange/packet. These should be used
when there is no client/server relationship between the two sides, or when that relationship is unknown.
This covers low-level network interactions (e.g. packet tracing) where you don't know if
there was a connection or which side initiated it.
This also covers unidirectional UDP flows and peer-to-peer communication where the
"user-facing" surface of the protocol / API does not expose a clear notion of client and server.

#### Source

<!-- semconv source -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `source.domain` | string | The domain name of the source system. [1] | `foo.example.com` | Recommended |
| `source.address` | string | Source address, for example IP address or Unix socket name. | `10.5.3.2` | Recommended |
| `source.port` | int | Source port number | `3389`; `2888` | Recommended |

**[1]:** This value may be a host name, a fully qualified domain name, or another host naming format.
<!-- endsemconv -->

#### Destination

Destination fields capture details about the receiver of a network exchange/packet.

<!-- semconv destination -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `destination.domain` | string | The domain name of the destination system. [1] | `foo.example.com` | Recommended |
| `destination.address` | string | Peer address, for example IP address or UNIX socket name. | `10.5.3.2` | Recommended |
| `destination.port` | int | Peer port number | `3389`; `2888` | Recommended |

**[1]:** This value may be a host name, a fully qualified domain name, or another host naming format.
<!-- endsemconv -->

### Network connection and carrier attributes

<!-- semconv network-connection-and-carrier -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `network.connection.type` | string | The internet connection type. | `wifi` | Recommended |
| `network.connection.subtype` | string | This describes more details regarding the connection.type. It may be the type of cell technology connection, but it could be used for describing details about a wifi connection. | `LTE` | Recommended |
| `network.carrier.name` | string | The name of the mobile carrier. | `sprint` | Recommended |
| `network.carrier.mcc` | string | The mobile carrier country code. | `310` | Recommended |
| `network.carrier.mnc` | string | The mobile carrier network code. | `001` | Recommended |
| `network.carrier.icc` | string | The ISO 3166-1 alpha-2 2-character country code associated with the mobile carrier network. | `DE` | Recommended |

`network.connection.type` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `wifi` | wifi |
| `wired` | wired |
| `cell` | cell |
| `unavailable` | unavailable |
| `unknown` | unknown |

`network.connection.subtype` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `gprs` | GPRS |
| `edge` | EDGE |
| `umts` | UMTS |
| `cdma` | CDMA |
| `evdo_0` | EVDO Rel. 0 |
| `evdo_a` | EVDO Rev. A |
| `cdma2000_1xrtt` | CDMA2000 1XRTT |
| `hsdpa` | HSDPA |
| `hsupa` | HSUPA |
| `hspa` | HSPA |
| `iden` | IDEN |
| `evdo_b` | EVDO Rev. B |
| `lte` | LTE |
| `ehrpd` | EHRPD |
| `hspap` | HSPAP |
| `gsm` | GSM |
| `td_scdma` | TD-SCDMA |
| `iwlan` | IWLAN |
| `nr` | 5G NR (New Radio) |
| `nrnsa` | 5G NRNSA (New Radio Non-Standalone) |
| `lte_ca` | LTE CA |
<!-- endsemconv -->

For `Unix` and `pipe`, since the connection goes over the file system instead of being directly to a known peer, `server.address` is the only attribute that usually makes sense (see description of `server.address` below).

## General remote service attributes

This attribute may be used for any operation that accesses some remote service.
Users can define what the name of a service is based on their particular semantics in their distributed system.
Instrumentations SHOULD provide a way for users to configure this name.

<!-- semconv peer -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `peer.service` | string | The [`service.name`](../../resource/semantic_conventions/README.md#service) of the remote service. SHOULD be equal to the actual `service.name` resource attribute of the remote service if any. | `AuthTokenCache` | Recommended |
<!-- endsemconv -->

Examples of `peer.service` that users may specify:

- A Redis cache of auth tokens as `peer.service="AuthTokenCache"`.
- A gRPC service `rpc.service="io.opentelemetry.AuthService"` may be hosted in both a gateway, `peer.service="ExternalApiService"` and a backend, `peer.service="AuthService"`.

## General identity attributes

These attributes may be used for any operation with an authenticated and/or authorized enduser.

<!-- semconv identity -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `enduser.id` | string | Username or client_id extracted from the access token or [Authorization](https://tools.ietf.org/html/rfc7235#section-4.2) header in the inbound request from outside the system. | `username` | Recommended |
| `enduser.role` | string | Actual/assumed role the client is making the request under extracted from token or application security context. | `admin` | Recommended |
| `enduser.scope` | string | Scopes or granted authorities the client currently possesses extracted from token or application security context. The value would come from the scope associated with an [OAuth 2.0 Access Token](https://tools.ietf.org/html/rfc6749#section-3.3) or an attribute value in a [SAML 2.0 Assertion](http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html). | `read:message, write:files` | Recommended |
<!-- endsemconv -->

These attributes describe the authenticated user driving the user agent making requests to the instrumented
system. It is expected this information would be propagated unchanged from node-to-node within the system
using the Baggage mechanism. These attributes should not be used to record system-to-system
authentication attributes.

Examples of where the `enduser.id` value is extracted from:

| Authentication protocol | Field or description            |
| :---------------------- | :------------------------------ |
| [HTTP Basic/Digest Authentication] | `username`               |
| [OAuth 2.0 Bearer Token] | [OAuth 2.0 Client Identifier] value from `client_id` for the [OAuth 2.0 Client Credentials Grant] flow and `subject` or `username` from get token info response for other flows using opaque tokens. |
| [OpenID Connect 1.0 IDToken] | `sub` |
| [SAML 2.0 Assertion] | `urn:oasis:names:tc:SAML:2.0:assertion:Subject` |
| [Kerberos] | `PrincipalName` |

| Framework               | Field or description            |
| :---------------------- | :------------------------------ |
| [JavaEE/JakartaEE Servlet] | `javax.servlet.http.HttpServletRequest.getUserPrincipal()` |
| [Windows Communication Foundation] | `ServiceSecurityContext.Current.PrimaryIdentity` |

[Authorization]: https://tools.ietf.org/html/rfc7235#section-4.2
[OAuth 2.0 Access Token]: https://tools.ietf.org/html/rfc6749#section-3.3
[SAML 2.0 Assertion]: http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html
[HTTP Basic/Digest Authentication]: https://tools.ietf.org/html/rfc2617
[OAuth 2.0 Bearer Token]: https://tools.ietf.org/html/rfc6750
[OAuth 2.0 Client Identifier]: https://tools.ietf.org/html/rfc6749#section-2.2
[OAuth 2.0 Client Credentials Grant]: https://tools.ietf.org/html/rfc6749#section-4.4
[OpenID Connect 1.0 IDToken]: https://openid.net/specs/openid-connect-core-1_0.html#IDToken
[Kerberos]: https://tools.ietf.org/html/rfc4120
[JavaEE/JakartaEE Servlet]: https://jakarta.ee/specifications/platform/8/apidocs/javax/servlet/http/HttpServletRequest.html
[Windows Communication Foundation]: https://docs.microsoft.com/en-us/dotnet/api/system.servicemodel.servicesecuritycontext?view=netframework-4.8

Given the sensitive nature of this information, SDKs and exporters SHOULD drop these attributes by
default and then provide a configuration parameter to turn on retention for use cases where the
information is required and would not violate any policies or regulations.

## General thread attributes

These attributes may be used for any operation to store information about
a thread that started a span.

<!-- semconv thread -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `thread.id` | int | Current "managed" thread ID (as opposed to OS thread ID). | `42` | Recommended |
| `thread.name` | string | Current thread name. | `main` | Recommended |
<!-- endsemconv -->

Examples of where `thread.id` and `thread.name` can be extracted from:

| Language or platform | `thread.id`                            | `thread.name`                      |
|-----------------------|----------------------------------------|------------------------------------|
| JVM                   | `Thread.currentThread().getId()`       | `Thread.currentThread().getName()` |
| .NET                  | `Thread.CurrentThread.ManagedThreadId` | `Thread.CurrentThread.Name`        |
| Python                | `threading.current_thread().ident`     | `threading.current_thread().name`  |
| Ruby                  | `Thread.current.object_id`             | `Thread.current.name`              |
| C++                   | `std::this_thread::get_id()`             |                                    |
| Erlang               | `erlang:system_info(scheduler_id)` |                                  |

## Source Code Attributes

Often a span is closely tied to a certain unit of code that is logically responsible for handling
the operation that the span describes (usually the method that starts the span).
For an HTTP server span, this would be the function that handles the incoming request, for example.
The attributes listed below allow to report this unit of code and therefore to provide more context
about the span.

<!-- semconv code -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `code.function` | string | The method or function name, or equivalent (usually rightmost part of the code unit's name). | `serveRequest` | Recommended |
| `code.namespace` | string | The "namespace" within which `code.function` is defined. Usually the qualified class or module name, such that `code.namespace` + some separator + `code.function` form a unique identifier for the code unit. | `com.example.MyHttpService` | Recommended |
| `code.filepath` | string | The source code file name that identifies the code unit as uniquely as possible (preferably an absolute file path). | `/usr/local/MyApplication/content_root/app/index.php` | Recommended |
| `code.lineno` | int | The line number in `code.filepath` best representing the operation. It SHOULD point within the code unit named in `code.function`. | `42` | Recommended |
| `code.column` | int | The column number in `code.filepath` best representing the operation. It SHOULD point within the code unit named in `code.function`. | `16` | Recommended |
<!-- endsemconv -->