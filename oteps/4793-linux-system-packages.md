# OpenTelemetry System Packages for Autoinstrumentations

Specify the structure and maintainership modus for system packages that deliver autoinstrumentations to applications running on hosts using a Debian- or RedHat-based Linux distribution.

## Motivation

Adopting OpenTelemetry can be a difficult task for most users without significant expertise in observability. Modifying applications to add and maintain SDKs and their setup is a chore that most developers would rather avoid. A lot of practitioners, and especially those without expert-level skills in observability (which is the overwhelming majority of people out there needing observability) are perfectly fine starting their observability journey by using auto-instrumentations, especially for those languages with good instrumentation coverage and mature SDKs.

Packaging the OpenTelemetry Injector and auto-instrumentations in system packages will provide an easy, satisfactory experience for users needing to monitor applications running on Linux-based (virtual) hosts. An “apt install opentelemetry“ experience that results in non-containerized applications monitored out of the box is going to allow ops personas to gain observability with a workflow they are familiar with.

## Explanation

You can monitor non-containerized applications running on a Linux host with a runtime supported by the [OpenTelemetry Injector](https://github.com/open-telemetry/opentelemetry-injector) by running:

```apt install opentelemetry```

(or the equivalent RPM command.)

If you are using a commercial observability vendor that provides their own distributions, you can replace the "community" packages installing distributions on your Linux hosts with those of the vendor.

The OpenTelemetry system packages respect all the usual mechanics in terms of delivering updates via package managers:

* Easy to add a trusted package repository to the Linux system
* Dependencies are resolved transparently by the package management system: for, when you have already installed the `opentelemetry` package and later add a runtime to your Linux system, e.g., a Java Virtual Machine, that can be automatically injected, you will be recommended (opt-in) to also install the OpenTelemetry autoinstrumentation package for Java.
* The packages integrate with system conventions: placing config files in expected locations (/etc), respecting FHS standards and including man pages.
* Uninstallation is clean and complete; using the Debian package ecosystem as an example, `apt remove opentelemetry` will eliminate all OpenTelemetry components and software, and `apt purge` will also remove configuration files.

## Internal details

The OpenTelemetry community makes available a variety of system packages:

* Each OpenTelemetry SDK that can injected at startup time via `LD_PRELOAD` ships its own "autoinstrumentation package", i.e., system packages that contain the SDK, its dependencies, and the default autoinstrumentations for the supported programming language. For example, for the OpenTelemetry Java Agent, this would be as simple as packaging the agent's JAR file with the right packaging relationships to the other OpenTelemetry system packages and, optionally, system JDKs.
* The OpenTelemetry Injector project ships the `opentelemetry-injector` package containing the `LD_PRELOAD` system object (`.so`) of the injector itself.
* The OpenTelemetry community also ships the `opentelemetry` is a so-called "metapackage" that consists exclusively of metadata that specify which other packages must be installed, that is, the OpenTelemetry Injector's and one or more autoinstrumentation packages.

These system packages are designed to work together: the OpenTelemetry Injector knows where to look for SDKs and autoinstrumentations available on the system via their respective system packages, and injects only the applications running on matching runtimes.

Autoinstrumentation packages are modelled in terms of metadata and file-system content so that vendor-specific distribution can be used as opposed to the community autoinstrumentation packages provided by the OpenTelemetry SDKs ("upstream" packages). This requires the existence of runtime-specific metapackages, like `opentelemetry-java-autoinstrumentation`, which are `provided` (using the `.deb` terminology) by both the upstream packages and vendor packages; additionally, vendor packages `replace` (using the `.deb` terminology) the upstream packages.

Autoinstrumentation packages delivering SDKs that support the [declarative configuration format](https://github.com/open-telemetry/opentelemetry-configuration) should integrate file-based configurations in their system package.

Injection of autoinstrumentations into applications is configurable by end users.
The OpenTelemetry Injector package offers, upon installation, a choice whether injecting applications is opt-in (default) or opt-out. In both cases, opting specific applications in or out is done via that application's process environment using a dedicated `OTEL_`-prefixed environment variable.

## Trade-offs and mitigations

While the system packages outlined in this OTEP can be used also to build container images, that is considered out of their intended scope.

Not all programming languages that have OpenTelemetry SDKs may be supported, e.g. Go, Rust or C++. There, a user may want to add the [OpenTelemetry eBPF Instrumentation](https://opentelemetry.io/docs/zero-code/obi/) to the mix.

The granularity of system packages in terms of the autoinstrumentations is going to be coarse, shipping all the "contrib" autoinstrumentations, and delegating the customization of which ones to activate to the declarative configuration files. While autoinstrumentation packages provide default configuration files, users are encouraged to add their own to the system and activate them using the process environment of the target applications.

The user experience of configuring the injected OpenTelemetry SDKs is going to be sub-par for applications running on runtimes with OpenTelemetry SDKs that do not support the declarative configuration format.

There is not going to be a risk of breaking applications by injecting applications with SDKs not present on the system: for example, passing `-javaagent:/non-existent.jar` prevents the Java Virtual Machine from starting. This is because the OpenTelemetry Injector already has mechanics to check for the existence of the required SDK files before triggering their injection into runtimes.

## Prior art and alternatives

The [Dash0 Operator](https://github.com/dash0hq/dash0-operator) has been using very similar mechanics (delivering an injector and autoinstrumentation files for various SDKs) on Kubernetes in production for more than year. The [OpenTelemetry Operator](https://github.com/open-telemetry/opentelemetry-operator/) also has injection mechanics processed runtime inside pods' containers, but the injection requires opt-in at the pod level via labels.

Considering the more larger goal of autoinstrumenting applications running on Linux hosts, the [OpenTelemetry eBPF Instrumentation](https://opentelemetry.io/docs/zero-code/obi/) fulfills a similar scope, with very different tradeoffs in terms of user experience including, but not limited to, configurability of SDK, coverage of instrumentations and supporting vendor distributions for specific runtimes.

## Open questions

How deep should we integrate the OpenTelemetry Collector system packages to work with the overall OpenTelemetry system package setup? For example, if an the OpenTelemetry Collector system package (`core` or `contrib`) is installed on the system, should the injected OpenTelemetry SDKs assume they should send telemetry to it? (This could be done, for example, by package installation scripts that update the defaults of the configuration files.)

## Prototypes

The OpenTelemetry Injector has a pre-release ["monolithic" system package](https://github.com/open-telemetry/opentelemetry-injector/releases/tag/v0.0.1-20251030) that installs the injector and various OpenTelemetry SDKs and their autoinstrumentations.

## Future possibilities

Integrate eBPF-based instrumentations for programming languages that cannot be injected via `LD_PRELOAD`, like Go, Rust or C++.
