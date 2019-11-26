# General attributes

The attributes described in this section are not specific to a particular operation but rather generic.
They may be used in any Span they apply to.
Particular operations may refer to or require some of these attributes.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [General network connection attributes](#general-network-connection-attributes)

<!-- tocstop -->

## General network connection attributes

These attributes may be used for any network related operation.
The `net.peer.*` attributes describe properties of the remote end of the network connection
(usually the transport-layer peer, e.g. the node to which a TCP connection was established),
while the `net.host.*` properties describe the local end.
In an ideal situation, not accounting for proxies, multiple IP addresses or host names,
the `net.peer.*` properties of a client are equal to the `net.host.*` properties of the server and vice versa.

|  Attribute name  |                                 Notes and examples                                |
| :--------------- | :-------------------------------------------------------------------------------- |
| `net.transport` | Transport protocol used. See note below.                                           |
| `net.peer.ip`   | Remote address of the peer (dotted decimal for IPv4 or [RFC5952][] for IPv6)       |
| `net.peer.port` | Remote port number as an integer. E.g., `80`.                                      |
| `net.peer.name` | Remote hostname or similar, see note below.                                        |
| `net.host.ip`   | Like `net.peer.ip` but for the host IP. Useful in case of a multi-IP host.         |
| `net.host.port` | Like `net.peer.port` but for the host port.                                        |
| `net.host.name` | Like `net.peer.name` but for the host name. If known, the name that the peer used to refer to the host should be preferred. For IP-based communication, an value obtained via an API like POSIX `gethostname` may be used as fallback. |

[RFC5952]: https://tools.ietf.org/html/rfc5952

**net.transport**: The name of the transport layer protocol (or the relevant protocol below the "application protocol"). Should be one of these strings:

* `IP.TCP`
* `IP.UDP`
* `IP`: Another IP-based protocol.
* `Unix`: Unix Domain socket.
* `pipe`: Named or anonymous pipe.
* `inproc`: Signals that there is only in-process communication not using a "real" network protocol in cases where network attributes would normally be expected. Usually all other network attributes can be left out in that case.
* `other`: Something else (not IP-based).

**net.peer.name**, **net.host.name**:
For IP-based communication, the name should be the host name that was used to look up the IP adress in `peer.ip`
(e.g., `"example.com"` if connecting to an URL `https://example.com/foo`).
If that is not available, reverse-lookup of the IP can be used to obtain it.
If `net.transport` is `"unix"` or `"pipe"`, the absolute path to the file representing it should be used.
If there is no such file (e.g., anonymous pipe),
the name should explicitly be set to the empty string to distinguish it from the case where the name is just unknown or not covered by the instrumentation.
