# Glossary

## User Definitions

- <a name="api-developer"></a>API Developer: A developer working on the
  OpenTelemetry API library for a particular language.
- <a name="sdk-developer"></a>SDK Developer: A developer working on implementing
  the logic either defined in the official SDK specification or a third party
  implementation. The implementation must be used only through the API by a
  library developer or application developer.
- <a name="library-developer"></a>Library Developer: This is a developer working
  on code that will be used by others. They are not creating a final deployable
  artifact and must only rely on the OpenTelemetry API as a dependency of their
  library. The library may have the express purpose of making another library
  observable (such libraries are called "integrations") or they may develop a
  library with any other purpose that has observability built in (e.g., a
  database client library that creates Spans itself when making database calls).
- <a name="app-developer"></a>Application Developer: An application developer is
  responsible for code that becomes a deployable artifact to run with some
  configuration by an operator. The application developer's project may depend
  on third party libraries that have been instrumented and may include its own
  libraries, making the application developer potentially a library developer as
  well. But only the end user, or operator, should include an OpenTelemetry SDK
  implementation as a dependency and configure, either through code or
  configuration files loaded by the program, the `TracerProvider` used by all libraries
  within the final program.
- <a name="operator"></a>Operator: The operator SHOULD be able to select a
  different SDK implementation, overriding the one chosed by the application
  developer.
