# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Cyber Incident Monitor Tool"
copyright = "2024, Daniel Vetrila"
author = "Daniel Vetrila"
root_doc = "index"  # Specify the root document for the project
today = '27 November 2024'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

latex_documents = [
    (
        root_doc,
        "cyberincidentmonitortool.tex",
        "Project Specification: AI-Powered Cyber Incident Monitoring Tool",  # Ensure this matches your actual project name
        "Daniel Vetrila (C00271021)",
        "manual",
    ),  # Changed from 'manual' to 'howto'
]

latex_elements = {
        'classoptions': ',openany', # Ensures chapters start on a new page (left or right)
                                    # Add ',oneside' if you also want page numbers
                                    # consistently on one side of the page: ',openany,oneside'
        'preamble': r'''
    \usepackage{tocloft}

    % --- Table of Contents Formatting for 'manual' (chapter/section) ---

    % Remove any automatic numbering or space reserved for it by LaTeX for ToC entries.
    % Your titles like "1. Introduction" and "1.1 Project Overview" will be the sole numbering.

    % For Chapters (Level 1 in your RST)
    \setlength{\cftchapnumwidth}{0pt}  % No space for \chapter numbers in ToC itself
    \renewcommand{\cftchappresnum}{}     % Text before chap number in ToC
    \renewcommand{\cftchapaftersnum}{}    % Text after chap num in ToC

    % For Sections (Level 2 in your RST, which are \subsections of chapters)
    \setlength{\cftsecnumwidth}{0pt}   % No space for \section numbers in ToC itself
    \renewcommand{\cftsecpresnum}{}      % Text before sec number in ToC
    \renewcommand{\cftsecaftersnum}{}     % Text after sec num in ToC

    % For Subsections (Level 3 in your RST, if you use them and they appear in ToC via :depth: 3)
    % \setlength{\cftsubsecnumwidth}{0pt}
    % \renewcommand{\cftsubsecpresnum}{}
    % \renewcommand{\cftsubsecaftersnum}{}

    % Optional: Adjust leader dots (e.g., remove them)
    % \renewcommand{\cftchapleader}{\hspace*{\fill}} % Chapter titles followed by space then page number
    % \renewcommand{\cftsecleader}{\hspace*{\fill}}  % Section titles followed by space then page number

    % Optional: Explicitly set indentation for ToC entries
    % \setlength{\cftchapindent}{0em}   % Chapter entries flush left
    % \setlength{\cftsecindent}{2em}     % Section entries indented (adjust '2em' as needed)
    % \setlength{\cftsubsecindent}{4em}  % Subsection entries indented further
    \setcounter{secnumdepth}{-2} % Or try 0 if -2 is too aggressive, but -2 usually stops all.


    % --- End of Table of Contents Formatting ---
    \date{27 November 2024}

    % Other general preamble settings
    \usepackage[utf8]{inputenc}
    \usepackage{amsmath}
    \usepackage{amsfonts}
    \usepackage{amssymb}
    \usepackage{graphicx}

    % This renews the \chapter command to ensure it clears to a new page
    % without necessarily going to an odd page (respects 'openany')
    % The standard 'report' and 'book' classes (used by 'manual') already do this
    % with \cleardoublepage by default if openright is active, or \clearpage if openany.
    % So, this explicit redefinition might not be strictly necessary if 'openany' works as expected.
    % \makeatletter
    % \renewcommand\chapter{\if@openright\cleardoublepage\else\clearpage\fi
    %                     \thispagestyle{plain}%
    %                     \global\@topnum\z@
    %                     \@afterindentfalse
    %                     \secdef\@chapter\@schapter}
    % \makeatother

    ''',
        # Other elements like 'papersize', 'pointsize' can go here
        # 'papersize': 'a4paper',
        # 'pointsize': '10pt',

        # 'fncychap' can be used with 'manual' if you like its chapter styling, e.g.:
        # 'fncychap': r'\usepackage[Sonny]{fncychap}',
    }

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
