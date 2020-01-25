# Semantic conventions for errors

This document defines semantic conventions for recording errors.

## Recording an Error

An error SHOULD be recorded as an `Event` on the span during which it occurred.
The name of the event MUST be `"error"`.

## Attributes

The table below indicates which attributes should be added to the `Event` and
their types.

| Attribute name | Type       | Notes and examples                                           | Required? |
| :------------- | :--------- | :----------------------------------------------------------- | :-------- |
| error.type     | String     | The type of the error. E.g. "Exception", "OSError"           | Yes       |
| error.message  | String     | The error message. E.g. `"Division by zero"`, `"Can't convert 'int' object to str implicitly"` | Yes       |
| error.stack    | Array\<String\> | A stack trace formatted as an array of strings. The stackframe at which the exeception occurred should be the first entry. E.g. `["Exception in thread \"main\" java.lang.RuntimeException: Test exception", "  at com.example.GenerateTrace.methodB(GenerateTrace.java:13)", "  at com.example.GenerateTrace.methodA(GenerateTrace.java:9)", "  at com.example.GenerateTrace.main(GenerateTrace.java:5)" ]` | No        |
