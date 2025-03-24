<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/profiles/_index.md
  to: profiles/README.md
--->

# Profiles

## Attribute handling exception

The resource attribute within the `code.*` namespace MUST NOT be utilized within the scope of the
OTel profiles signal. This constraint is imposed to prevent redundancy and maintain data integrity.
The OTel profiles signal is specifically designed to efficiently encode stacktraces and symbolization
information, rendering the inclusion of resource attributes within the `code.*` namespace unnecessary
and potentially duplicative. Consequently, this attribute is explicitly excluded from use within the
context of OTel profiles.
