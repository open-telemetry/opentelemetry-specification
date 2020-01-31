# Semantic conventions for logs and errors

This document defines semantic conventions for recording logs and errors.

## Recording a Log

A log SHOULD be recorded as an `Event` on the span during which it occurred.
The name of the event MUST be `"log"`.

## Attributes

The table below indicates which attributes should be added to the `Event` and
their types.

| Attribute name | Type       | Notes and examples                                           | Required? |
| :------------- | :--------- | :----------------------------------------------------------- | :-------- |
| log.type | String | The source of the log message such as `syslog`, `log4j`, or `log` if the source is unknown | Yes |
| log.severity | String | One of `debug`, `info`, `warn`, `error`, `fatal`, and `panic` | Yes |
| log.message | String | The log message. E.g. `"User not found"` or `"json.Marshal failed"`. | Yes |
| frame.file | String | Filename where the log occurred, e.g. `main.go` | No |
| frame.line | uint32 | Line number where the log occurred, e.g. `10` | No |
| frame.func | String | Function name where the log occurred, e.g. `method1` | No |
| frame.stack | String | An array of stackframes formatted as JSON. The stackframe at which the log occurred should be the first entry. E.g. `[{"func": "method1", "file": "main.go", "line": 10}, {"func": "main", "file": "main.go", "line": 5}]` | No |

## Recording an Error

An error SHOULD be recorded as an `Event` on the span during which it occurred.
The name of the event MUST be `"error"`.

## Attributes

The table below indicates which attributes should be added to the `Event` and
their types.

| Attribute name | Type       | Notes and examples                                           | Required? |
| :------------- | :--------- | :----------------------------------------------------------- | :-------- |
| log.type | String | The type of the error (its fully-qualified class name, if applicable). E.g. "java.net.ConnectException", "OSError" | Yes |
| log.severity | String | One of `error`, `fatal`, and `panic` | Yes |
| log.message | String | The error message. E.g. `"Division by zero"`, `"Can't convert 'int' object to str implicitly"` | Yes |
| frame.file | String | Filename where the error occurred, e.g. `main.go` | No |
| frame.line | uint32 | Line number where the error occurred, e.g. `10` | No |
| frame.func | String | Function name where the error occurred, e.g. `method1` | No |
| frame.stack | String | An array of stackframes formatted as JSON. The stackframe at which error log occurred should be the first entry. E.g. `[{"func": "method1", "file": "main.go", "line": 10}, {"func": "main", "file": "main.go", "line": 5}]` | No |
