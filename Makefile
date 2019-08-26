# All documents to be used in spell check.
ALL_DOC := $(shell find . -name '*.md' -type f | sort)

TOOLS_DIR := ./.tools
MISSPELL_BINARY=$(TOOLS_DIR)/misspell

.PHONY: precommit
precommit: install-misspell misspell

 .PHONY: install-misspell
install-misspell: go.mod go.sum internal/tools.go
	go build -o $(MISSPELL_BINARY) github.com/client9/misspell/cmd/misspell

 .PHONY: misspell
misspell:
	$(MISSPELL_BINARY) -error $(ALL_DOCS)

 .PHONY: misspell-correction
misspell-correction:
	$(MISSPELL_BINARY) -w $(ALL_DOCS)