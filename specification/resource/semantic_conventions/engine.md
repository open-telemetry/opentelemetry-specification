# Engine

**type:** `engine`

**Description:** Resource describing the packaged software running the application code. Engines are executed using process.runtime.

<!-- semconv engine_resource -->
| Attribute  | Type | Description  | Example  | Required |
|---|---|---|---|---|
| `engine.name` | string | The name of the engine. | `FildFly` | Yes |
| `engine.version` | string | The version of the engine, as returned by the engine (preferably during runtime) without modification. | `21.0.0` | No |
| `engine.description` | string | Additional description about the engine. | `WildFly Full 21.0.0.Final (WildFly Core 13.0.1.Final) - 2.2.2.Final` | No |
<!-- endsemconv -->

Information describing the engine SHOULD be captured using the values acquired from the API provided by the engine, preferably during runtime, to avoid maintenance burden on engine version upgrades.

A resource can be attributed to at most one engine. To illustrate, let's look at a Python application using Apache HTTP Server with mod_wsgi as the server and Django as the web framework. In this case:

* Apache HTTP Server would be set as `process.runtime`
* `mod_wsgi` would be set as engine
* Django would not be set as an engine (Django is not running on `process.runtime`).

## Java Engines:

Java engines are often but not always packaged as application servers. For Java application servers supporting Servlet API the required information MAY be captured by invoking `ServletContext.getServerInfo()` during runtime and parsing the result.

Java engines SHOULD use the following for `engine.name` attribute. If none of the listed values apply, custom value MAY be used:

| Name | `engine.name` |
|---|---|
| Apache Tomcat | tomcat |
| Jetty | jetty |
| Oracle Weblogic | weblogic |
| IBM Websphere | websphere  |
| WildFly | wildfly |
| JBoss EAP | jboss |
| Caucho Resin | resin |
| Apache TomEE | tomee |
| Apache Geronimo | geronimo |
| JOnAS | jonas |

## .NET engines:

TBD: Add examples such as IIS/ASP.NET/.NET CORE and Mono

## Python engines:

TBD: Add examples such as uWSGI and gunicorn

## PHP engines

TBD: Add examples such as FPM and mod_php
