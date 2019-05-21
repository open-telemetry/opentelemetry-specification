### Census Server Stats

The encoding is based on [BinaryEncoding](BinaryEncoding.md)

#### Fields added in Census Server Stats version 0

##### LB-Latency-Ns

* optional
* `field_id` = 0
* `len` = 8

Request processing latency observed on Load Balance. The unit is nanoseconds.
It is int64 little endian.

##### Server-Latency_Ns

* optional
* `field_id` = 1
* `len` = 8

Request processing latency observed on Server. The unit is nanoseconds.
It is int64 little endian.

##### Trace-Options

* optional
* `field_id` = 2
* `len` = 1

It is a 1-byte representing a 8-bit unsigned integer. The least significant
bit provides if the request was sampled on the server or not (1= sampled,
0= not sampled).

The behavior of other bits is currently undefined.

#### Valid example (Hex)
{`0,`
  `0, 38, C7, 0, 0, 0, 0, 0, 0,`
  `1, 50, C3, 0, 0, 0, 0, 0, 0,`
  `2, 1`}

This corresponds to:
* `lb_latency_ns` = 51000 (0x000000000000C738)
* `server_latency_ns` = 50000 (0x000000000000C350)
* `trace_options` = 1 (0x01)

