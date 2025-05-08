# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "AI-Powered Cyber Incident Monitoring Tool"
copyright = "2025"
author = "Daniel Vetrila"
today = "April 7, 2025"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.githubpages",
    "sphinxcontrib.plantuml",
    "sphinxcontrib.mermaid",
]
plantuml = "java -jar /usr/share/java/plantuml/plantuml.jar"
mermaid_cmd = '/usr/bin/mmdc'  # Default global install path
mermaid_params = ['--theme', 'neutral', '--width', '1600', '--backgroundColor', 'white']

mermaid_params = [
    '--puppeteerConfigFile', 'docs/mermaid_config/puppeteer_config.json',
    '--width', '1600',
    '--theme', 'neutral'
]


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# -- Options for LaTeX output ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    "figure_align": "htbp",
    "extraclassoptions": "openany,oneside",
    "preamble": r"""
        \usepackage{graphicx}
        \usepackage{float}
        \usepackage{hyperref}
        \usepackage{titlesec}
        \usepackage{tocloft}
        \usepackage{adjustbox}
        \newcommand{\mermaidwidth}{\linewidth}
        
        % Fix section numbering in TOC
        \renewcommand{\numberline}[1]{}
        
        % Adjust section numbering format
        \renewcommand{\thesection}{\arabic{section}}
        \renewcommand{\thesubsection}{\arabic{section}.\arabic{subsection}}
        \renewcommand{\thesubsubsection}{\arabic{section}.\arabic{subsection}.\arabic{subsubsection}}
        
        % Adjust section title formatting
        \titleformat{\section}{\normalfont\Large\bfseries}{\thesection}{1em}{}
        \titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection}{1em}{}
        \titleformat{\subsubsection}{\normalfont\normalsize\bfseries}{\thesubsubsection}{1em}{}
        
        % Adjust TOC formatting
        \renewcommand{\cftsecnumwidth}{2.5em}
        \renewcommand{\cftsubsecnumwidth}{3.5em}
        \renewcommand{\cftsubsubsecnumwidth}{4.5em}
        
        % Remove dots in TOC
        \renewcommand{\cftdot}{}
        \renewcommand{\cftdotsep}{0}
        
        % Fix TOC entry formatting
        \renewcommand{\cftsecpresnum}{\thesection\hspace{0.5em}}
        \renewcommand{\cftsubsecpresnum}{\thesubsection\hspace{0.5em}}
        \renewcommand{\cftsubsubsecpresnum}{\thesubsubsection\hspace{0.5em}}
        
        % Remove automatic numbering in TOC
        \renewcommand{\cftsecfont}{\normalfont}
        \renewcommand{\cftsubsecfont}{\normalfont}
        \renewcommand{\cftsubsubsecfont}{\normalfont}

        
    """,
}

# -- Options for PDF output -------------------------------------------------
latex_documents = [
    (
        "index",
        "AI-Powered_Cyber_Incident_Monitoring_Tool.tex",
        "AI-Powered Cyber Incident Monitoring Tool Documentation",
        author,
        "manual",
    ),
]

# -- Options for autodoc extension ------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# -- Options for intersphinx extension --------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "fastapi": ("https://fastapi.tiangolo.com/", None),
}

# -- Options for todo extension --------------------------------------------
todo_include_todos = True

# -- Options for Napoleon extension ----------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# -- Options for viewcode extension ----------------------------------------
viewcode_follow_imports_members = True

# -- Options for HTMLHelp output ------------------------------------------
htmlhelp_basename = "AIPoweredCyberIncidentMonitoringToolDoc"

# -- Options for Epub output ----------------------------------------------
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ["search.html"]

def setup(app):
    app.add_css_file('custom.css')
