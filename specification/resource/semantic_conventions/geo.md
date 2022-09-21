# Geo

**Status**: [Experimental](../../document-status.md)

**type:** `geo`

**Description**: Geo fields can carry data about a specific location related to a resource or event. This geolocation information can be derived from techniques such as Geo IP, or be user-supplied.

<!-- semconv geo -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `geo.city_name` | string | City name. | `Montreal`; `Berlin` | Recommended |
| `geo.continent_code` | string | Two-letter code representing continent’s name. | `AF` | Recommended |
| `geo.continent_name` | string | Name of the continent. | `North America`; `Europe` | Recommended |
| `geo.country_iso_code` | string | Two-letter ISO Country Code (ISO 3166-1 alpha2). | `CA` | Recommended |
| `geo.country_name` | string | Country name. | `Canada` | Recommended |
| `geo.location.lon` | double | Longitude of the geo location. | `-73.61483` | Recommended |
| `geo.location.lat` | double | Latitude of the geo location. | `45.505918` | Recommended |
| `geo.name` | string | User-defined description of a location. [1] | `boston-dc` | Recommended |
| `geo.postal_code` | string | Postal code associated with the location. Values appropriate for this field may also be known as a postcode or ZIP code and will vary widely from country to country. | `94040` | Recommended |
| `geo.region_iso_code` | string | Region ISO code (ISO 3166-2). | `CA-QC` | Recommended |
| `geo.region_name` | string | Region name. | `Quebec` | Recommended |
| `geo.timezone` | string | The time zone of the location, such as IANA time zone name. | `America/Argentina/Buenos_Aires` | Recommended |

**[1]:** User-defined description of a location, at the level of granularity they care about. Could be the name of their data centers, the floor number, if this describes a local physical entity, city names. Not typically used in automated geolocation.

`geo.continent_code` MUST be one of the following:

| Value  | Description |
|---|---|
| `AF` | Africa |
| `AN` | Antarctica |
| `AS` | Asia |
| `EU` | Europe |
| `NA` | North America |
| `OC` | Oceania |
| `SA` | South America |
<!-- endsemconv -->
