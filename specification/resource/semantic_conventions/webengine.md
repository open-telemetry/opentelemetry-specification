# Webengine

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**Status**: [Experimental](../../document-status.md)

**type:** `webengine`

**Description:** Resource describing the packaged software running the application code. Web engines are typically executed using process.runtime.

<!-- semconv webengine_resource -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `webengine.name` | string | The name of the web engine. | `WildFly` | Required |
| `webengine.version` | string | The version of the web engine. | `21.0.0` | Recommended |
| `webengine.description` | string | Additional description of the web engine (e.g. detailed version and edition information). | `WildFly Full 21.0.0.Final (WildFly Core 13.0.1.Final) - 2.2.2.Final` | Recommended |
<!-- endsemconv -->

Information describing the web engine SHOULD be captured using the values acquired from the API provided by the web engine, preferably during runtime, to avoid maintenance burden on engine version upgrades. As an example - Java engines are often but not always packaged as application servers. For Java application servers supporting Servlet API the required information MAY be captured by invoking `ServletContext.getServerInfo()` during runtime and parsing the result.

A resource can be attributed to at most one web engine.

The situations where there are multiple candidates, it is up to instrumentation library authors to choose the web engine. To illustrate, let's look at a Python application using Apache HTTP Server with mod_wsgi as the server and Django as the web framework. In this situation:

* Either Apache HTTP Server or `mod_wsgi` MAY be chosen as `webengine`, depending on the decision made by the instrumentation authors.
* Django SHOULD NOT be set as an `webengine` as the required information is already available in instrumentation library and setting this into `webengine` would duplicate the information.
