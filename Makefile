# All documents to be used in spell check.
ALL_DOC := $(shell find . -name '*.md' -type f | sort)

MISSPELL=misspell -error
MISSPELL_CORRECTION=misspell -w

.PHONY: travis-ci
travis-ci: misspell

.PHONY: misspell
misspell:
	$(MISSPELL) $(ALL_DOC)

.PHONY: misspell-correction
misspell-correction:
	$(MISSPELL_CORRECTION) $(ALL_DOC)

.PHONY: install-tools
install-tools:
	GO111MODULE=on go install \
	  github.com/client9/misspell/cmd/misspell
