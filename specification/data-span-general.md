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
| `net.transport` | Transport protocol used. See [note below](#net.transport).                         |
| `net.peer.ip`   | Remote address of the peer (dotted decimal for IPv4 or [RFC5952][] for IPv6)       |
| `net.peer.port` | Remote port number as an integer. E.g., `80`.                                      |
| `net.peer.name` | Remote hostname or similar, see [note below](#net.name).                           |
| `net.host.ip`   | Like `net.peer.ip` but for the host IP. Useful in case of a multi-IP host.         |
| `net.host.port` | Like `net.peer.port` but for the host port.                                        |
| `net.host.name` | Local hostname or similar, see [note below](#net.name).                            |

[RFC5952]: https://tools.ietf.org/html/rfc5952

<a name="net.transport"></a>

### `net.transport` attribute

This attribute should be set to the name of the transport layer protocol (or the relevant protocol below the "application protocol"). One of these strings should be used:

* `IP.TCP`
* `IP.UDP`
* `IP`: Another IP-based protocol.
* `Unix`: Unix Domain socket. See note below.
* `pipe`: Named or anonymous pipe. See note below.
* `inproc`: Signals that there is only in-process communication not using a "real" network protocol in cases where network attributes would normally be expected. Usually all other network attributes can be left out in that case.
* `other`: Something else (not IP-based).

For `Unix` and `pipe`, since the connection goes over the file system instead of being directly to a known peer, `net.peer.name` is the only attribute that usually makes sense (see description of `net.peer.name` below).

<a name="net.name"></a>

### `net.*.name` attributes

For IP-based communication, the name should be a DNS host name.
For `net.peer.name`, this should be the name that was used to look up the IP address that was connected to
(i.e., matching `net.peer.ip` if that one is set; e.g., `"example.com"` if connecting to an URL `https://example.com/foo`).
If only the IP address but no host name is available, reverse-lookup of the IP may optionally be used to obtain it.
`net.host.name` should be the host name of the local host,
preferably the one that the peer used to connect for the current operation.
If that is not known, a public hostname should be preferred over a private one. However, in that case it may be redundant with information already contained in resources and may be left out.
It will usually not make sense to use reverse-lookup to obtain `net.host.name`, as that would result in static information that is better stored as resource information.

If `net.transport` is `"unix"` or `"pipe"`, the absolute path to the file representing it should be used as `net.peer.name` (`net.host.name` doesn't make sense in that context).
If there is no such file (e.g., anonymous pipe),
the name should explicitly be set to the empty string to distinguish it from the case where the name is just unknown or not covered by the instrumentation.
