# Security Policy

This security policy applies to all projects under the [open-telemetry organization][gh-organization] on GitHub. Security reports involving specific projects should still be reported following the instructions on this document: the report will be shared by the technical committee to the project leads, who might not all have access to the private key required to decrypt your message.

## Supported Versions

The OpenTelemetry project provides community support only for the last minor version: bug fixes are released either as part of the next minor version or as an on-demand patch version. Independent of which version is next, all patch versions are cumulative, meaning that they represent the state of our `master` branch at the moment of the release. For instance, if the latest version is 0.10.0, bug fixes are released either as part of 0.11.0 or 0.10.1.

Security fixes are given priority and might be enough to cause a new version to be released.

## Reporting a Vulnerability

If you find something suspicious and want to report it, we'd really appreciate!

### Ways to report

* It is preferable to always encrypt your message, no matter the channel you choose to report the issue
* Send a message to [cncf-opentelemetry-tc@lists.cncf.io][mailing-list]
* If you can't send an email, either open an issue on GitHub with the description or open a pull request on GitHub with a reproducer and/or fix. We really prefer if you'd talk to us per email, though, as our repositories are public and we would like to give a heads up to our users before disclosing it publicly.

### Our PGP key

No matter what channel you choose to communicate with us, we would prefer you to encrypt your message using our [published key][published-key], which is available on all major key servers and should match the one shown below. If you are new to PGP, you can run the following command to encrypt a file called "message.txt":

1. Receive our keys from the key server:

    `gpg --keyserver pool.sks-keyservers.net --recv-keys 936EAAD588D07C19`

2. Encrypt a "message.txt" file into "message.txt.asc":

    `gpg -ea -r 936EAAD588D07C19 message.txt`

3. Send us the resulting "message.txt.asc"

**Our published key should match this one:**

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
mQGNBF9pFvUBDACyv9icULbqaOmy8iYAgrHlwcfpShYmi4TI/ykYxXo6PlYdh9Px
7jG9qZQyemdhtK07Mn/xOVMHuJUzVLevGZc4hRJdd1mDKacyz0KW3yn9aN79iLG2
Q7D/5WoRVconeyTuhVOaCoi3srP8XH/UAneArMyr9oIHKEWtoInIEtR4NFZ6uKUO
0gpdUdo+aQFwU+j0OFAz+pxddLo2QblSvSuKPbPJhMalGTg4+4NdMlr4xK6ehF9k
X3CkGjK3UsJCD2URrHzH6RjWv9sC4Z9bX0PRkSzO20h8fBCLwLB9QZcTlv7heRnm
Mn7a8kLej+XYgwixYMlrdrWhaMuEmQ/ePInf1gG24LTf3r1TePPsQzE7NN5wy+k8
CYY1N9lhNOrsGYvQp+N7kmpe2YjlEM6oPkFilvinXEJvHgHZN41NPTVwM8MvjYC8
kLinltT2SkX2SswgASkisFJGbIVunTV4mKViIdP/2W/5gmMzZ4PI2qktm1C2JIRh
kyk5O4fMQp8EK3UAEQEAAbR/T3BlblRlbGVtZXRyeSBUZWNobmljYWwgQ29tbWl0
dGVlIChFbmNyeXB0aW9uIGtleSBmb3IgcmVwb3J0aW5nIHNlY3VyaXR5IHZ1bG5l
cmFiaWxpdGllcykgPGNuY2Ytb3BlbnRlbGVtZXRyeS10Y0BsaXN0cy5jbmNmLmlv
PokB1AQTAQgAPhYhBMxumTKSJeJaajSNGpNuqtWI0HwZBQJfaRb1AhsDBQkSzAMA
BQsJCAcCBhUKCQgLAgQWAgMBAh4BAheAAAoJEJNuqtWI0HwZACUL/3KG92XtKu7D
nypOY5HWw4UqlHa3gdUe2dsJiFCaz9QEPDxdK2BsLn69nrhFMy88iqcB1Xndt5Kb
7JjaN0cVmFm2yzic7BEpnZ3qW9f0mGjgJCVpOOezo0nnEO53oT4/4QKbW52gHglk
ytGhwlmygJlDvIxchJ/XTZnl/LpCaedy/ezvSvpLoGfPB/I3J1qPu+M8eJWDQQtO
buRwSY8zYfPjk9WVX6X4Y3/upPNWSROFIgf+koPwKfDM8DycLz2ke4hVLD4RsHJM
52dCFBdXqtuTx/O2Ojz/p/r5LYK5uVR0rjfFqGf8l+g0WL0HLg2zo0ABU82TBozn
AraBd164fP71OaXBOJLx3jdNkhZHiokQi7fFBwoDCJ41fte59eZ8vO4NWHVbxXm+
ug+rU4Id+uMtYOv7z+ei8JmOfwZXwXKgIH8I81vj3pi+yO7qtAR7GzQci9Ev8Rda
36sidbATHSBxlNjfStqZ7KuAJ6B2il6P0PbHS/its4EHd4L8ur9PHbkBjQRfaRb1
AQwArd3S5xwj+ddAOV4aGmX2PjE/i372KeuOZD/QXU1WhiP6zl4FJVo6UM8cJ6ia
66zBrkCIgQ+C2z4JOJPuLf/RuMRffbiwpsI2KJTkerlMZKXfrBVQrRhQxKhImW9W
5VhY6/+PGS2c/vgzMswo0Ae1Z9/CPtkpu1t/RNCaOAoB2lUIlGiB37JqFqnq5KHl
ZO5WsAYwEhc2k0fFJEpLyncKFjfQsZgkUJmiIqHNLYkV6E+lgFxpf715nQOsws64
o+EWS2BjHZMVnVBhKXauiUl6p6Ts/iBD0wltyUuxGCZBSdqxZtwxwENqvwxbjghS
IWAA2nkaFjpT6ti/cD3Bfa9/xVR5s/fWNIdfCkMQKgNk8jLDgcvNzF9IZxbm6YyO
tOo9zw3vKlz4/CP7tiHMJN3zLNgoeN6Zd3TuxPGD3JglJ8v1S7LFez3VopOkiejP
oKUC92QSeqau7aRmlgNT7pWCkQfsnMt5+jWYUxOXzOgakGwBtiev3zIVpyUDiZwH
9wiDABEBAAGJAbwEGAEIACYWIQTMbpkykiXiWmo0jRqTbqrViNB8GQUCX2kW9QIb
DAUJEswDAAAKCRCTbqrViNB8GSTlC/0U8lTD9MfKcGcYe+kKJymugHbP8Q68p9u9
+FnOaZO6pA00a5EQ37JDlhDunKMBGhHX6i9on/VZ6LuxCyKrEdN+HJFPdcLmDOIv
0+IqPiqmnAeKFn6onUqk3/jeFGxyIIIfhw9w/X0PD8an4Zk1efQpXMnI4u9Ncd5y
8qOg1w5nvp8bUcwwaMGgni6SepSEswik4cGJpGJsxnZuooeGpa2UcwQvGmM0YqXe
iJCijxxwaVh5yyKQMoD6Cl7geNCDsm8H6a846EV8fnQOigzhfbT6YCtiS3IR0yb+
cu2z17f35XJd8RKnA1UPBVHdfHnx8fNTf3IQLfTU9v6Gh8MwcJvXFIFA+76Ki4tB
nkxxmKo5bx7EkeUnDQXXGj3dualMTDcW84+JMA7Y8FqKYfi4JytE6vFHzX4ZiLP7
PPNFxvdSTsNUJtSpGgFOx/QIl+01WztBVFJsLGDsA9LS4GZa7Sdp6oEfKlXgrtPB
n4pJoVqhDTDWzKSuNrL3uWvRSMDi2yo=
=cD84
-----END PGP PUBLIC KEY BLOCK-----
```

[gh-organization]: https://github.com/open-telemetry
[published-key]: http://pool.sks-keyservers.net/pks/lookup?op=get&search=0x936EAAD588D07C19
[mailing-list]: https://lists.cncf.io/g/cncf-opentelemetry-tc
[gitter-room]: https://gitter.im/open-telemetry/community
