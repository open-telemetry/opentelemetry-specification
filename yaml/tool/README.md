## Tables

Semantic convention tables MUST be generated from the [yaml files](../trace/).
To do so, we have written a python tool that can be installed by opening the [source directory](./)
and running the following command (preferably in a Python virtual environment / venv):

```bash
python setup.py develop
```

After the tool is installed, tables can be generated using the command:

```bash
gen-semconv --yaml-root {yaml_folder} markdown --markdown-root {markdown_folder}
```

Where `{yaml_folder}` is the absolute path to the directory containing the yaml files (`yaml` folder
in this repository) and `{markdown_folder}` the absolute path to the directory containing the
markdown definitions (`specification` folder in this repository).

The tool will automatically replace the tables with the up to date definition of the semantic conventions.
To do so, the tool looks for special tags in the markdown.

```
<!-- semconv {semantic_convention_id} -->
<!-- endsemconv -->
```

Everything between these two tags will be replaced with the table definition.
The `{semantic_convention_id}` MUST be the `id` field in the yaml files of the semantic convention
for which we want to generate the table.
After `{semantic_convention_id}`, optional parameters enclosed in parentheses can be added to customize the output:

- `tag={tag}`: prints only the attributes that have `{tag}` as a tag;
- `full`: prints attributes and constraints inherited from the parent semantic conventions or from included ones;
- `ref`: prints attributes that are referenced from another semantic convention;
- `remove_constraint`: does not print additional constraints of the semantic convention.

### Examples

These examples assume that a semantic convention with the id `http.server` extends another semantic convention with the id `http`.

`<!-- semconv http.server -->` will print only the attributes and constraints of the `http.server` semantic
convention.

`<!-- semconv http.server(full) -->` will print the attributes and constraints of the `http` semantic
convention and also the attributes and constraints of the `http.server` semantic convention.

`<!-- semconv http.server() -->` is equivalent to `<!-- semconv http.server -->`.

`<!-- semconv http.server(tag=network) -->` will print the constraints and attributes of the `http.server` semantic
convention that have the tag `network`.

`<!-- semconv http.server(tag=network, full) -->` will print the constraints and attributes of both `http` and `http.server`
semantic conventions that have the tag `network`.