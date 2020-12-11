# All documents to be used in spell check.
ALL_DOCS := $(shell find . -name '*.md' -not -path './.github/*' -type f | grep -v ^./node_modules | sort)
PWD := $(shell pwd)

TOOLS_DIR := ./internal/tools
MISSPELL_BINARY=bin/misspell
MISSPELL = $(TOOLS_DIR)/$(MISSPELL_BINARY)
MARKDOWN_LINK_CHECK=markdown-link-check
MARKDOWN_LINT=markdownlint


.PHONY: install-misspell
install-misspell:
	cd $(TOOLS_DIR) && go build -o $(MISSPELL_BINARY) github.com/client9/misspell/cmd/misspell

.PHONY: misspell
misspell:
	$(MISSPELL) -error $(ALL_DOCS)

.PHONY: misspell-correction
misspell-correction:
	$(MISSPELL) -w $(ALL_DOCS)

.PHONY: install-markdown-link-check
install-markdown-link-check:
	npm install -g $(MARKDOWN_LINK_CHECK)

.PHONY: markdown-link-check
markdown-link-check:
	@for f in $(ALL_DOCS); do $(MARKDOWN_LINK_CHECK) --quiet --config .markdown_link_check_config.json $$f; done

.PHONY: install-markdownlint
install-markdownlint:
	npm install -g markdownlint-cli

.PHONY: markdownlint
markdownlint:
	@echo $(ALL_DOCS)
	@for f in $(ALL_DOCS); do echo $$f; $(MARKDOWN_LINT) -c .markdownlint.yaml $$f || exit 1;	done

.PHONY: table-generation
table-generation:
	docker run --rm -v $(PWD)/semantic_conventions:/source -v $(PWD)/specification:/spec otel/semconvgen -f /source markdown -md /spec
