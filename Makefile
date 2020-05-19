# All documents to be used in spell check.
ALL_DOCS := $(shell find . -name '*.md' -type f | grep -v ^./node_modules | sort)

TOOLS_DIR := ./.tools
MISSPELL_BINARY=$(TOOLS_DIR)/misspell
MARKDOWN_LINK_CHECK=markdown-link-check

.PHONY: install-misspell
install-misspell:
	go build -o $(MISSPELL_BINARY) github.com/client9/misspell/cmd/misspell

.PHONY: misspell
misspell:
	$(MISSPELL_BINARY) -error $(ALL_DOCS)

.PHONY: misspell-correction
misspell-correction:
	$(MISSPELL_BINARY) -w $(ALL_DOCS)

.PHONY: install-markdown-link-check
install-markdown-link-check:
	npm install -g $(MARKDOWN_LINK_CHECK)

.PHONY: markdown-link-check
markdown-link-check:
	$(MARKDOWN_LINK_CHECK) --quiet $(ALL_DOCS)

.PHONY: install-markdown-lint
install-markdown-lint:
	npm install -g markdownlint-cli

.PHONY: markdown-lint
markdown-lint:
	markdownlint -c .markdownlint.yaml '**/*.md'
