## Contributing

Contributions are welcome!

### Setup for local development

Clone the repository and install dependencies (example using a virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Run tests:

```bash
python manage.py test
```

### Working on documentation

This project uses **MkDocs** for documentation.

Install the docs tooling:

```bash
pip install mkdocs mkdocs-material
```

Serve the docs locally:

```bash
mkdocs serve
```

Then open `http://127.0.0.1:8000/` in your browser.

### Submitting changes

- Fork the repository.
- Create a feature branch.
- Add or update tests and documentation where appropriate.
- Open a pull request with a clear description of your changes.


