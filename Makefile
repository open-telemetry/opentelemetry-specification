PWD := $(shell pwd)

# see https://github.com/open-telemetry/build-tools/releases for semconvgen updates
# Keep links in semantic_conventions/README.md and .vscode/settings.json in sync!
SEMCONVGEN_VERSION=0.17.0

# TODO: add `yamllint` step to `all` after making sure it works on Mac.
.PHONY: all
all: install-tools markdownlint markdown-link-check cspell

.PHONY: cspell
cspell:
	@if ! npm ls cspell; then npm install; fi
	npx cspell --no-progress

.PHONY: markdown-link-check
markdown-link-check:
	docker run --rm \
		--mount 'type=bind,source=$(PWD),target=/home/repo' \
		lycheeverse/lychee:sha-8222559@sha256:6f49010cc46543af3b765f19d5319c0cdd4e8415d7596e1b401d5b4cec29c799 \
		--config home/repo/.lychee.toml \
		--root-dir /home/repo \
		-v \
		home/repo

    # check that all links to opentelemetry.io are canonical (no redirects)
    # see https://github.com/open-telemetry/opentelemetry-specification/pull/4554
	docker run --rm \
		--mount 'type=bind,source=$(PWD),target=/home/repo' \
		lycheeverse/lychee:sha-8222559@sha256:6f49010cc46543af3b765f19d5319c0cdd4e8415d7596e1b401d5b4cec29c799 \
		--config home/repo/.lychee.toml \
		--root-dir /home/repo \
		--max-redirects 0 \
		--include '^https://opentelemetry.io/.*' \
		--exclude '' \
		-v \
		home/repo

# This target runs markdown-toc on all files that contain
# a comment <!-- tocstop -->.
#
# The recommended way to prepate a .md file for markdown-toc is
# to add these comments:
#
#   <!-- toc -->
#   <!-- tocstop -->
.PHONY: markdown-toc
markdown-toc:
	@if ! npm ls markdown-toc; then npm install; fi
	@for f in $(ALL_DOCS); do \
		if grep -q '<!-- tocstop -->' $$f; then \
			echo markdown-toc: processing $$f; \
			npx --no -- markdown-toc --no-first-h1 --no-stripHeadingTags -i $$f || exit 1; \
		else \
			echo markdown-toc: no TOC markers, skipping $$f; \
		fi; \
	done

.PHONY: markdownlint
markdownlint:
	@if ! npm ls markdownlint; then npm install; fi
	@for f in $(ALL_DOCS); do \
		echo $$f; \
		npx --no -p markdownlint-cli markdownlint -c .markdownlint.yaml $$f \
			|| exit 1; \
	done

.PHONY: install-yamllint
install-yamllint:
    # Using a venv is recommended
	pip install -U yamllint~=1.26.1

.PHONY: yamllint
yamllint:
	yamllint .

# Run all checks in order of speed / likely failure.
.PHONY: check
check: cspell markdownlint markdown-link-check
	@echo "All checks complete"

# Generate spec compliance matrix from YAML source
.PHONY: compliance-matrix
compliance-matrix:
	pip install -U PyYAML
	python .github/scripts/compliance_matrix.py
	@echo "Compliance matrix generation complete"

.PHONY: install-tools
install-tools:
	npm install
	@echo "All tools installed"
