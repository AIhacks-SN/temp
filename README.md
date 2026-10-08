# Product feedback explorer

This standalone Streamlit template displays a small product-feedback explorer backed by checked-in synthetic fixture data. It does not need credentials, external services, or access to production data.

Filter the bundled feedback by product, optionally upload an additional CSV with the same columns to extend the table for the current browser session (nothing is written to disk), and download the currently filtered rows as CSV.

## Prerequisites

- Python 3.12
- uv

`.tool-versions` records the Python patch and uv release used for reproducibility. It is a reference for any version manager you use, not a requirement to install a particular version manager.

Check the installed versions:

```sh
python --version
uv --version
```

## Run locally

From this directory, install the locked dependencies and start the app with:

```sh
uv run --locked streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in a browser. Stop the app with Ctrl-C. Run the same command again to restart it.

The fixture is intentionally synthetic and local. No credentials or network-backed data source are required.
