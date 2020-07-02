# Semantic conventions for exceptions

This document defines semantic conventions for recording exceptions.

## Recording an Exception

An exception SHOULD be recorded as an `Event` on the span during which it occurred.
The name of the event MUST be `"exception"`.

## Attributes

The table below indicates which attributes should be added to the `Event` and
their types.

| Attribute name    | Type   | Notes and examples                                                                                                                                                                                                                                                                                                                                      | Required? |
| :---------------- | :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------- |
| exception.type    | String | The type of the exception (its fully-qualified class name, if applicable). E.g. "java.net.ConnectException", "OSError"                                                                                                                                                                                                                                  | Yes       |
| exception.message | String | The exception message. E.g. `"Division by zero"`, `"Can't convert 'int' object to str implicitly"`                                                                                                                                                                                                                                                      | Yes       |
| stacktrace        | String | A stack trace as a string in the natural representation in the language runtime. E.g. `"Exception in thread \"main\" java.lang.RuntimeException: Test exception\n at com.example.GenerateTrace.methodB(GenerateTrace.java:13)\n at com.example.GenerateTrace.methodA(GenerateTrace.java:9)\n at com.example.GenerateTrace.main(GenerateTrace.java:5)"`. | No        |
| log.severity      | String | The severity of the error E.g. `Fatal`, `Error`, `Warn`, etc.                                                                                                                                                                                                                                                                                           |
