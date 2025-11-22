# All documents to be used in spell check.
ALL_DOCS := $(shell find . -type f -name '*.md' -not -path './.github/*' -not -path './node_modules/*' -not -name 'spec-compliance-matrix.md' | sort)
PWD := $(shell pwd)

# Detect Python and pip commands
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)
PIP := $(shell command -v pip3 2>/dev/null || command -v pip 2>/dev/null)

# Validate Python and pip are available
.PHONY: check-python
check-python:
	@if [ -z "$(PYTHON)" ]; then \
		echo "Error: Python is not installed. Please install Python (Python 3 recommended)."; \
		exit 1; \
	fi
	@if [ -z "$(PIP)" ]; then \
		echo "Error: pip is not installed. Please install pip."; \
		exit 1; \
	fi

# see https://github.com/open-telemetry/build-tools/releases for semconvgen updates
# Keep links in semantic_conventions/README.md and .vscode/settings.json in sync!
SEMCONVGEN_VERSION=0.17.0

# TODO: add `yamllint` step to `all` after making sure it works on Mac.
.PHONY: all
all: install-tools markdownlint markdown-link-check cspell

.PHONY: cspell
cspell:
	npx cspell --no-progress --config .cspell.yaml $(ALL_DOCS)

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
install-yamllint: check-python
    # Using a venv is recommended
	$(PIP) install -U yamllint~=1.26.1

.PHONY: yamllint
yamllint:
	yamllint .

# Run all checks in order of speed / likely failure.
.PHONY: check
check: cspell markdownlint markdown-link-check
	@echo "All checks complete"

# Generate spec compliance matrix from YAML source
.PHONY: compliance-matrix
compliance-matrix: check-python
	$(PIP) install -U PyYAML
	$(PYTHON) .github/scripts/compliance_matrix.py
	@echo "Compliance matrix generation complete"

.PHONY: install-tools
install-tools:
	npm install
	@echo "All tools installed"
