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

Information describing the engine SHOULD be captured using the values acquired from the API provided by the engine, preferably during runtime, to avoid maintenance burden on engine version upgrades. As an example - Java engines are often but not always packaged as application servers. For Java application servers supporting Servlet API the required information MAY be captured by invoking `ServletContext.getServerInfo()` during runtime and parsing the result.

A resource can be attributed to at most one engine.

The situations where there are multiple candidates, it is up to instrumentation library authors to choose the engine. To illustrate, let's look at a Python application using Apache HTTP Server with mod_wsgi as the server and Django as the web framework. In this case:

* Either Apache HTTP Server or `mod_wsgi` MAY be chosen as `engine`, depending on the decision made by the instrumentation authors.
* Django would SHOULD NOT be set as an engine as the required information is already available in insrumentation library and setting this into `engine` would duplicate the information.
