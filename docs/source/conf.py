# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Dykes"
copyright = "2026, Piper Thunstrom"
author = "Piper Thunstrom"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#FF8B1A",
        "color-brand-content": "#FF3863",
        "color-brand-visited": "#3B94DD",
    },
    "dark_css_variables": {
        "color-brand-primary": "#FF8B1A",
        "color-brand-content": "#FF3863",
        "color-brand-visited": "#3B94DD",
    },
}
html_static_path = ["_static"]
