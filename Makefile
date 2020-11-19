# All documents to be used in spell check.
ALL_DOCS := $(shell find . -name '*.md' -not -path './.github/*' -type f | grep -v ^./node_modules | sort)
PWD := $(shell pwd)

TOOLS_DIR := ./.tools
MISSPELL_BINARY=$(TOOLS_DIR)/misspell
MARKDOWN_LINK_CHECK=markdown-link-check
MARKDOWN_LINT=markdownlint


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
	@for f in $(ALL_DOCS); do $(MARKDOWN_LINK_CHECK) --quiet --config .markdown_link_check_config.json $$f; done

.PHONY: install-markdownlint
install-markdown-lint:
	npm install -g markdownlint-cli

.PHONY: markdownlint
markdown-lint:
	@echo $(ALL_DOCS)
	@for f in $(ALL_DOCS); do echo $$f; $(MARKDOWN_LINT) -c .markdownlint.yaml $$f || exit 1;	done

.PHONY: table-generation
table-generation:
	docker run --rm -v $(PWD)/semantic_conventions:/source -v $(PWD)/specification:/spec otel/semconvgen -f /source markdown -md /spec
