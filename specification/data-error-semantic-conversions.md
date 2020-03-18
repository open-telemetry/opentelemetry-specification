# Semantic conventions for errors

This document defines semantic conventions for recording logs and errors.

## Recording an Error
Errors and exceptions SHOULD be recorded any time an unhandled exception or error leaves the boundary of a span. 

An error event created by an API call SHOULD be associated with the current span from which the API call is made. 

