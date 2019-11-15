# Glossary

## User Definitions

- <a name="api-developer"></a>API Developer: A developer working on the API
  library for a particular language.
- <a name="sdk-developer"></a>SDK Developer: A developer working on implementing
  the logic either defined in the official SDK specification or a third party
  implementation. The implementation must be used only through the API by a
  library developer or end user.
- <a name="library-developer"></a>Library Developer: This is a developer working
  on code that will be used by others. They are not creating a final
  deployable artifact and must only rely on the OpenTelemetry API as a
  dependency of their library.
- <a name="end-user"></a>End User: An end user is responsible for code that
  becomes a deployable artifact to run with some configuration by
  an operator. The end user's project may depend on third party libraries that
  have been instrumented and may include its own libraries, making the end
  user potentially a library developer as well. But only the end user, or
  operator, may include an OpenTelemetry SDK implementation as a dependency and
  configure, either through code or configuration files loaded by the program,
  the `Tracer` used by all libraries within the final program.
- <a name="operator"></a>Operator:
