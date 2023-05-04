# Semantic conventions for TLS spans

**Status**: [Experimental](../../document-status.md)

This document defines semantic conventions for TLS/SSL client and server Spans.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Common Attributes](#common-attributes)
- [Client attributes](#client-attributes)
- [Server attributes](#server-attributes)

<!-- tocstop -->

## Common Attributes

These attributes may be used for base information of any TLS/SSL encrypted communication.

<!-- semconv tls -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `tls.version` | string | Numeric part of the version parsed from the original string of the negotiated [SSL/TLS protocol version](https://www.openssl.org/docs/man1.1.1/man3/SSL_get_version.html#RETURN-VALUES) | `1.2`; `3` | Required |
| `tls.version_protocol` | string | Normalized lowercase protocol name parsed from original string of the negotiated [SSL/TLS protocol version](https://www.openssl.org/docs/man1.1.1/man3/SSL_get_version.html#RETURN-VALUES) | `ssl` | Required |
| `tls.cipher` | string | String indicating the [cipher](https://datatracker.ietf.org/doc/html/rfc5246#appendix-A.5) used during the current connection. | `TLS_RSA_WITH_3DES_EDE_CBC_SHA`; `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256` | Opt-In |
| `tls.curve` | string | String indicating the curve used for the given cipher, when applicable | `secp256r1` | Opt-In |
| `tls.established` | boolean | Boolean flag indicating if the TLS negotiation was successful and transitioned to an encrypted tunnel. | `True` | Opt-In |
| `tls.next_protocol` | string | String indicating the protocol being tunneled. Per the values in the [IANA registry](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#alpn-protocol-ids), this string should be lower case. | `http/1.1` | Opt-In |
| `tls.resumed` | boolean | Boolean flag indicating if this TLS connection was resumed from an existing TLS negotiation. | `True` | Opt-In |

`tls.version_protocol` MUST be one of the following:

| Value  | Description |
|---|---|
| `ssl` | ssl |
| `tls` | tls |
| `unknown` | unknown |
<!-- endsemconv -->

The values allowed for `tls.cipher` MUST be one of the `Descriptions` of the [registered TLS Cipher Suits](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#table-tls-parameters-4).

## Client attributes

The following additional attributes describe the client participating in secure communication.

<!-- semconv tls.client -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `tls.client.certificate` | string | PEM-encoded stand-alone certificate offered by the client. This is usually mutually-exclusive of `client.certificate_chain` since this value also exists in that list. | `MII...` | Opt-In |
| `tls.client.certificate_chain` | string[] | Array of PEM-encoded certificates that make up the certificate chain offered by the client. This is usually mutually-exclusive of `client.certificate` since that value should be the first certificate in the chain. | `[MII..., MI...]` | Opt-In |
| `tls.client.issuer` | string | Distinguished name of [subject](https://datatracker.ietf.org/doc/html/rfc5280#section-4.1.2.6) of the issuer of the x.509 certificate presented by the client. | `CN=Example Root CA, OU=Infrastructure Team, DC=example, DC=com` | Opt-In |
| `tls.client.ja3` | string | A hash that identifies clients based on how they perform an SSL/TLS handshake. | `d4e5b18d6b55c71272893221c96ba240` | Opt-In |
| `tls.client.not_after` | string | Date/Time indicating when client certificate is no longer considered valid. | `2021-01-01T00:00:00.000Z` | Opt-In |
| `tls.client.not_before` | string | Date/Time indicating when client certificate is first considered valid. | `1970-01-01T00:00:00.000Z` | Opt-In |
| `tls.client.server_name` | string | Also called an SNI, this tells the server which hostname to which the client is attempting to connect to. | `opentelemetry.io` | Opt-In |
| `tls.client.subject` | string | Distinguished name of subject of the x.509 certificate presented by the client. | `CN=myclient, OU=Documentation Team, DC=example, DC=com` | Opt-In |
| `tls.client.hash.md5` | string | Certificate fingerprint using the MD5 digest of DER-encoded version of certificate offered by the client. For consistency with other hash values, this value should be formatted as an uppercase hash. | `0F76C7F2C55BFD7D8E8B8F4BFBF0C9EC` | Opt-In |
| `tls.client.hash.sha1` | string | Certificate fingerprint using the SHA1 digest of DER-encoded version of certificate offered by the client. For consistency with other hash values, this value should be formatted as an uppercase hash. | `9E393D93138888D288266C2D915214D1D1CCEB2A` | Opt-In |
| `tls.client.hash.sha256` | string | Certificate fingerprint using the SHA256 digest of DER-encoded version of certificate offered by the client. For consistency with other hash values, this value should be formatted as an uppercase hash. | `0687F666A054EF17A08E2F2162EAB4CBC0D265E1D7875BE74BF3C712CA92DAF0` | Opt-In |
<!-- endsemconv -->

## Server attributes

The following additional attributes describe the server participating in secure communication.

<!-- semconv tls.server -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `tls.server.certificate` | string | PEM-encoded stand-alone certificate offered by the server. This is usually mutually-exclusive of `server.certificate_chain` since this value also exists in that list. | `MII...` | Opt-In |
| `tls.server.certificate_chain` | string[] | Array of PEM-encoded certificates that make up the certificate chain offered by the server. This is usually mutually-exclusive of `server.certificate` since that value should be the first certificate in the chain. | `[MII..., MI...]` | Opt-In |
| `tls.server.issuer` | string | Distinguished name of [subject](https://datatracker.ietf.org/doc/html/rfc5280#section-4.1.2.6) of the issuer of the x.509 certificate presented by the client. | `CN=Example Root CA, OU=Infrastructure Team, DC=example, DC=com` | Opt-In |
| `tls.server.ja3s` | string | A hash that identifies servers based on how they perform an SSL/TLS handshake. | `d4e5b18d6b55c71272893221c96ba240` | Opt-In |
| `tls.server.not_after` | string | Date/Time indicating when server certificate is no longer considered valid. | `2021-01-01T00:00:00.000Z` | Opt-In |
| `tls.server.not_before` | string | Date/Time indicating when server certificate is first considered valid. | `1970-01-01T00:00:00.000Z` | Opt-In |
| `tls.server.subject` | string | Distinguished name of subject of the x.509 certificate presented by the server. | `CN=myserver, OU=Documentation Team, DC=example, DC=com` | Opt-In |
| `tls.server.hash.md5` | string | Certificate fingerprint using the MD5 digest of DER-encoded version of certificate offered by the server. For consistency with other hash values, this value should be formatted as an uppercase hash. | `0F76C7F2C55BFD7D8E8B8F4BFBF0C9EC` | Opt-In |
| `tls.server.hash.sha1` | string | Certificate fingerprint using the SHA1 digest of DER-encoded version of certificate offered by the server. For consistency with other hash values, this value should be formatted as an uppercase hash. | `9E393D93138888D288266C2D915214D1D1CCEB2A` | Opt-In |
| `tls.server.hash.sha256` | string | Certificate fingerprint using the SHA256 digest of DER-encoded version of certificate offered by the server. For consistency with other hash values, this value should be formatted as an uppercase hash. | `0687F666A054EF17A08E2F2162EAB4CBC0D265E1D7875BE74BF3C712CA92DAF0` | Opt-In |
<!-- endsemconv -->
