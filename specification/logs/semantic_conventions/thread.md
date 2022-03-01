# Thread attributes

**Status**: [Experimental](../../document-status.md)

These attributes may be used to store information about a thread that emitted a log.

| Attribute     | Type   | Description                                               | Examples | Required |
|---------------|--------|-----------------------------------------------------------|----------|----------|
| `thread.id`   | int    | Current "managed" thread ID (as opposed to OS thread ID). | `42`     | No       |
| `thread.name` | string | Current thread name.                                      | `main`   | No       |

Examples of where `thread.id` and `thread.name` can be extracted from:

| Launguage or platform | `thread.id`                            | `thread.name`                      |
|-----------------------|----------------------------------------|------------------------------------|
| JVM                   | `Thread.currentThread().getId()`       | `Thread.currentThread().getName()` |
| .NET                  | `Thread.CurrentThread.ManagedThreadId` | `Thread.CurrentThread.Name`        |
| Python                | `threading.current_thread().ident`     | `threading.current_thread().name`  |
| Ruby                  |                                        | `Thread.current.name`              |
| C++                   | `std::this_thread::get_id()`           |                                    |
| Erlang                | `erlang:system_info(scheduler_id)`     |                                    |
