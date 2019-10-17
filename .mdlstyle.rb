all

# Multiple headings with the same content allowed for sibling headings
rule 'MD024', :allow_different_nesting => true

# Ordered lists should have increasing prefixes
rule 'MD029', :style => :ordered

# Ignore unordered list style
exclude_rule 'MD004'

# Ignore line length
exclude_rule 'MD013'

# Inline HTML
exclude_rule 'MD033'

# Fenced code blocks should have a language specified
exclude_rule 'MD040'
