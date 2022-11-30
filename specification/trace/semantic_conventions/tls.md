# Semantic conventions for TLS spans

**Status**: [Experimental](../../document-status.md)

This document defines semantic conventions for TLS/SSL client and server Spans.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

<!-- tocstop -->

## Common Attributes

These attributes may be used for base information of any TLS/SSL encrypted communication.

<!-- semconv tls -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `tls.protocol` | string | The negotiated [SSL/TLS protocol version](https://www.openssl.org/docs/man1.1.1/man3/SSL_get_version.html#RETURN-VALUES) of the current connection. | `SSLv3` | Recommended |
| `tls.authorized` | boolean | true, if the peer certificate was signed by one of the CAs specified when creating the socket, otherwise false. | `True` | Recommended |

`tls.protocol` MUST be one of the following:

| Value  | Description |
|---|---|
| `SSLv3` | sslv3 |
| `TLSv1` | tlsv1 |
| `TLSv1.1` | tlsv1.1 |
| `TLSv1.2` | tlsv1.2 |
| `TLSv1.3` | tlsv1.3 |
| `unknown` | unknown |
<!-- endsemconv -->

## Cipher suite attributes

These attributes may be used for details on the negotiated cipher suite.

<!-- semconv tls.cipher -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `tls.cipher.name` | string | [IETF name of the cipher suite](https://datatracker.ietf.org/doc/html/rfc5246#appendix-A.5) | `TLS_RSA_WITH_3DES_EDE_CBC_SHA`; `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` | Recommended |
<!-- endsemconv -->

The values allowed for `tls.cipher.name` MUST be one of the `Descriptions` of the [registered TLS Cipher Suits](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#table-tls-parameters-4).

## Certificate attributes

These attributes may be used for any operation for details on the certificates.
Fingerprints and serial numbers MUST be provided as strings of uppercase hexadecimal numbers with every two characters (every byte) separated by colon (`:`), e.g. `04:C8:04:4B:BB:F2:4E:2B:7A:37:25:91:64:00:54:95:91:2C`.
This is a widely-used notation by CLI tools like `openssl` or browsers to display those certificate details.'

<!-- semconv tls.certificate -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `tls.peer.certificate.subject` | string | The peer [certificate subject](https://datatracker.ietf.org/doc/html/rfc5280#section-4.1.2.6) | `C=US, ST=California, L=San Francisco, O=OpenTelemetry, Inc, CN=*.opentelemetry.io` | Recommended |
| `tls.peer.certificate.fingerprint` | string | The SHA-1 digest of the DER encoded peer certificate | `95:B4:D0:6E:CD:C1:2C:22:92:B8:CD:26:54:79:E4:84:E3:47:34:2E` | Recommended |
| `tls.peer.certificate.fingerprint256` | string | The SHA-256 digest of the DER encoded peer certificate | `10:5A:86:67:BC:22:43:55:62:88:21:31:1B:93:F0:62:7F:05:F2:D8:EE:19:C6:F3:D6:BB:60:91:DD:ED:95:D1` | Recommended |
| `tls.peer.certificate.serial_number` | string | The peer [certificate serial number](https://datatracker.ietf.org/doc/html/rfc5280#section-4.1.2.2), as a hex string | `04:C8:04:4B:BB:F2:4E:2B:7A:37:25:91:64:00:54:95:91:2C` | Recommended |
| `tls.peer.certificate.not_before` | string | The date-time the peer certificate is valid from. | `Mar 9 00:00:00 2021 GMT` | Recommended |
| `tls.peer.certificate.not_after` | string | The date-time after which the peer certificate is no longer valid. | `Mar 1 23:59:59 2022 GMT` | Recommended |
| `tls.host.certificate.subject` | string | The host certificate [certificate subject](https://datatracker.ietf.org/doc/html/rfc5280#section-4.1.2.6) | `C=US, ST=California, L=San Francisco, O=OpenTelemetry, Inc, CN=*.opentelemetry.io` | Recommended |
| `tls.host.certificate.fingerprint` | string | The SHA-1 digest of the DER encoded host certificate | `95:B4:D0:6E:CD:C1:2C:22:92:B8:CD:26:54:79:E4:84:E3:47:34:2E` | Recommended |
| `tls.host.certificate.fingerprint256` | string | The SHA-256 digest of the DER encoded host certificate | `95:B4:D0:6E:CD:C1:2C:22:92:B8:CD:26:54:79:E4:84:E3:47:34:2E` | Recommended |
| `tls.host.certificate.serial_number` | string | The host certificate [certificate serial number](https://datatracker.ietf.org/doc/html/rfc5280#section-4.1.2.2), as a hex string | `04:C8:04:4B:BB:F2:4E:2B:7A:37:25:91:64:00:54:95:91:2C` | Recommended |
| `tls.host.certificate.not_before` | string | The date-time the host certificate is valid from. | `Mar 9 00:00:00 2021 GMT` | Recommended |
| `tls.host.certificate.not_after` | string | The date-time after which the peer certificate is no longer valid. | `Mar 1 23:59:59 2022 GMT` | Recommended |
<!-- endsemconv -->