import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "AI Cyber Monitor"
copyright = "2024, Your Name"
author = "Your Name"

release = "1.0"


# Enable automatic section numbering
numfig = True
numfig_format = {"section": "Section %s"}

# Enable cross-references between documents
autosectionlabel_prefix_document = True


extensions = [
    "sphinx.ext.autosectionlabel",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.plantuml",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# html_theme = "sphinx_rtd_theme"
html_theme = "furo"
html_theme_options = {
    "light_css_variables": {
        # Modern color scheme
        "color-brand-primary": "#2563eb",  # Modern blue
        "color-brand-secondary": "#4f46e5",  # Indigo
        "color-brand-content": "#3b82f6",
        "color-api-name": "#4f46e5",
        "color-api-pre-name": "#3b82f6",
        "color-link": "#3b82f6",
        # Typography
        "font-stack": "'Space Grotesk', system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
        "font-stack--monospace": "'JetBrains Mono', monospace",
        # Layout
        "sidebar-item-spacing-vertical": "0.4rem",
        "content-padding": "2rem",
        "gradient-primary": "linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)",
    },
    "dark_css_variables": {
        "color-brand-primary": "#818cf8",
        "color-brand-secondary": "#6366f1",
        "color-brand-content": "#818cf8",
        "color-background-primary": "#0f172a",  # Dark navy
        "color-background-secondary": "#1e293b",
    },
    # Modern features
    "top_of_page_button": "edit",
    "navigation_with_keys": True,
    "announcement": "<em>🚀 Next-gen cyber threat intelligence platform</em>",
}

html_static_path = ["_static"]

html_css_files = [
    "css/modern.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
]


# html_theme_options = {"style_nav_header_background": "#2A4D6E", "titles_only": False}

plantuml = "java -jar /usr/share/java/plantuml/plantuml.jar"
mermaid_version = "10.9.0"
