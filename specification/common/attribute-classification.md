# Classification via Attributes

**Status**: [Experimental](../document-status.md)

From Wikipedia:
> Classification is a process related to categorization, the process in which
> ideas and objects are recognized, differentiated and understood.

Attributes are sometimes recorded to indicate the class of the entity that is
emitting the telemetry or the class of the activity that is reported by
telemetry, in other words to _classify_ the entity or the activity.

There are usually 2 ways to classify using attributes, described below.

## Classification Via Attribute Value

The first classification approach is to record the class as a value of some
attribute.

For example we can record an attribute named `component` with a value of
`database` (`component=database` for short) to indicate that the telemetry is
from a database and `component=httpserver` to indicate that the telemetry is
from an HTTP server. This approach allows to classify via the _value_ of the
attribute.

Note the limitation of this approach: it classifies across a dimension and we
need to give this dimension a clear name (which is the attribute name) and allow
recording only a single fact across this dimension (because each attribute can
have only one value). In our example if we wanted to also record the fact that
the emitting component is a VM (and not a physical host), we cannot use
`component=vm` although it may be reasonable to say that a VM is a type of a
component. With this approach when a database is running on a VM we simply
cannot record this fact because we have to simultaneously have both
`component=vm` and `component=database` recorded and that's impossible.

To resolve this dilema we of course could try to split the `component` attribute
into 2 separate attributes (or dimensions), for example `machine_type` and
`software_component` but it is often very difficult to find appropriate
descriptive names for such attributes. We know that we have a database on a VM,
but what is the collective name of a domain of values that "database" belongs to
or the collective name of a domain of values that "VM" belongs to? To overcome
this problem the classification via presence is used.

## Classification Via Attribute Presence

The second classification approach is to indicate the class of the entity or
activity via the _presence_ of a particular attribute.

For example to record that the activity is with a database we can record an
attribute named `db.name`. Mere presence of such attribute, regardless of the
value of the attribute is an indication that the activity is about a database.
We no longer need to come up with a collective name for all "things, one of
which is a database".

Note that classification via presence allows to classify the same entity or
activity across multiple dimensions simultaneously, as many as there are
attributes that are _present_. To record that a database is on a VM we will have
2 attributes present: `db.name` and `vm.hypervisor`, each recording some useful
information.

## Choosing Classification Approach

Based on limitations described above let's look into some examples that show
when the classification should be done via the value and when classification
should be done via the presence of the attribute.

For example let's assume we want to record a query against a database that
serves requests via an http protocol (i.e. the database is implemented as an
http server). If we used classification via value of attribute `component` we
would have a hard time recording this information because we would need to
simultaneously record that `component=database` and `component=httpserver` which
is impossible. With classification via presence this is easily doable by
recording 2 attributes named `db.name` and `http.server_name`, each attribute
having a value in that particular dimension of classification. If in addition we
also want to record that the database is running on a VM, we can easily add
another attribute such as `vm.hypervisor=esx` without affecting in any way the
other 2 recorded facts.

Now let's consider a case when classification by value is the right approach.
This typically happens when the class is the only fact that we need to record
and no additional information needs to be recorded using possibly different
attributes for each class. Let's illustrate this on an example.

We want to record information about databases. A database is a type of an
entity, so we introduce an attribute the presence of which classifies the entity
as a database, e.g. `db.system`. The presence of this attribute indicates that
we have a database.

Next, we want to classify the type of the database, i.e. whether it is a
PostgreSQL or MySQL. We can record the database type as the value of the
attribute `db.system=postgresql`. Note that in this case one attribute
`db.system` participates both in classification by presence and in
classification by value (it records 2 facts: that the entity is a database and
the fact that the database type is PostgreSQL).

Using `db.system=postgresql` for classification by value is a correct approach
because _there is no further information_ necessary to be recorded specifically
for PostgreSQL. If _there was such a need_, for example if we also needed to
record the PostgreSQL version number then instead we would choose to record the
fact that the database is a PostgreSQL by presence of for example attribute
`db.postgres.version` (in which case we no longer need to store "postgresql" in
`db.system` although there is no harm in doing so).

A litmus test that helps to see when an attribute is incorrectly doing
classification by value is the following:

If you record any sort of information about an entity using an attribute where
the value of the attribute is one from a finite set (from enumeration) and you
also need one or more additional attributes to record other facts about that
entity then you are likely incorrectly doing classification by value. This is
especially clearly visible if the names of the additional attributes may be
different depending on the value of the classifying attribute. For example,
(`component=database` and `db.name`) pair of attributes matches this litmus
test. It is easy to see that in such cases the first attribute (`component`)
that does the classification by value is superfluous. Dropping it will result in
a single attribute (`db.name`) recorded using classification by presence
approach.
