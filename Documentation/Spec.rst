.. default-role:: literal

.. _table-of-contents:
  
Table of Contents
=================
    
.. contents::
   :local:
   :depth: 3
    
----

.. _introduction:

1. Introduction
===============

.. _project-overview:

1.1. Project Overview
---------------------

This document provides comprehensive documentation for the AI-Powered Cyber Incident Monitoring Tool, a sophisticated system designed to automate the collection, analysis, and reporting of cybersecurity threats. The tool leverages cutting-edge technologies including Google's Gemini AI, ThreatFox API, and the MITRE ATT&CK framework to provide real-time threat intelligence and analysis.

.. _background:

1.2. Background and Motivation
-----------------------------

The cybersecurity landscape is constantly evolving, with threats becoming more sophisticated and frequent. Traditional manual threat monitoring and analysis methods are no longer sufficient to keep pace with these challenges. This project was born from the need to:

* Automate the labor-intensive process of threat monitoring
* Provide real-time analysis of potential threats
* Integrate multiple threat intelligence sources
* Generate actionable insights for security teams
* Reduce response time to emerging threats

.. _objectives:

1.3. Project Objectives
----------------------

The primary objectives of this project were to:

* Develop an automated threat monitoring system
* Implement AI-powered IOC analysis
* Create a user-friendly web interface
* Provide comprehensive threat reporting
* Ensure system reliability and scalability

.. _scope:

1.4. Scope
----------

**In Scope:**

*   Development of data collection modules for specified web sources (e.g., NewsNow, ThreatPost RSS).

*   Integration with Google Gemini AI for IOC extraction from text and AI-driven analysis.

*   Integration with ThreatFox API for IOC enrichment.

*   Mapping of threat data to the MITRE ATT&CK framework (utilizing a local cache of MITRE data).

*   Development of a web interface (using FastAPI, Jinja2) to display:

    *   Monitored articles and extracted IOCs.
    *   Detailed analysis reports for IOCs and articles.
    *   Real-time updates via WebSockets.
    *   Manual IOC submission and analysis.
    *   PCAP file analysis for IOC presence.

*   Development of a basic CLI for:

    *   IOC analysis and report generation.
    *   (Potentially) Triggering article monitoring tasks.

*   Automated HTML report generation for IOCs.

*   Local caching mechanism for MITRE ATT&CK data.

*   Basic logging and error handling.

**Out of Scope (for initial version):**

*   Advanced user authentication and role-based access control (RBAC) for the web interface.

*   Sophisticated, customizable threat ranking based on detailed organizational profiles.

*   Active blocking or remediation capabilities.

*   Distributed deployment and high-availability clustering.

*   Machine learning model training for custom IOC detection (relies on Gemini for this).

*   Extensive support for a wide array of data sources beyond the initially specified ones.

----

.. _requirements:

2. Requirements
===============

.. _functional-requirements:

2.1. Functional Requirements
----------------------------

.. list-table:: Functional Requirements
   :widths: 10 40 10 40
   :header-rows: 1

   * - ID
     - Requirement Description
     - Priority
     - Justification
   * - FR01
     - The system shall automatically collect articles from pre-defined web sources (NewsNow, ThreatPost RSS).
     - High
     - Core function for obtaining raw threat intelligence.
   * - FR02
     - The system shall extract potential IOCs (IPs, URLs, domains, file hashes) from collected articles using regex and AI.
     - High
     - Essential for identifying actionable threat indicators.
   * - FR03
     - The system shall query the ThreatFox API to enrich identified IOCs with available threat data.
     - High
     - Provides crucial context and details about known threats.
   * - FR04
     - The system shall utilize the Gemini AI API to perform detailed analysis of IOCs and generate structured summaries.
     - High
     - Provides advanced analytical capabilities and human-readable insights.
   * - FR05
     - The system shall utilize the Gemini AI API to analyze full article content and provide structured summaries.
     - Medium
     - Enhances understanding of broader threat contexts from articles.
   * - FR06
     - The system shall map enriched IOC data to relevant MITRE ATT&CK techniques and tactics.
     - High
     - Standardizes threat description and aids in understanding attacker methodologies.
   * - FR07
     - The system shall generate HTML reports for analyzed IOCs, including AI summary, ThreatFox data, and MITRE mapping.
     - High
     - Core deliverable for presenting findings to users.
   * - FR08
     - The web interface shall display a dashboard of recently monitored articles and their status.
     - High
     - Provides an overview of current threat landscape being monitored.
   * - FR09
     - The web interface shall allow users to click on an article to view its content and any AI-generated analysis.
     - High
     - Enables users to drill down into specific threat information.
   * - FR10
     - The web interface shall allow users to manually submit an IOC for analysis.
     - High
     - Provides flexibility for analyzing specific IOCs not automatically picked up.
   * - FR11
     - The web interface shall display the detailed HTML report for any analyzed IOC.
     - High
     - User access to analysis results.
   * - FR12
     - The web interface shall use WebSockets to provide real-time updates for new articles and analyses.
     - Medium
     - Enhances user experience by providing timely information without manual refreshes.
   * - FR13
     - The system shall allow checking for the presence of a given IOC within a provided PCAP/PCAPNG file.
     - Medium
     - Adds capability to correlate external threats with local network activity.
   * - FR14
     - The system shall maintain a local cache of the MITRE ATT&CK enterprise framework data, refreshable periodically.
     - Medium
     - Improves performance and reduces external dependency for MITRE mapping.
   * - FR15
     - The CLI shall allow users to submit an IOC for analysis and receive a report (text or path to HTML).
     - Medium
     - Caters to users preferring command-line operations or scripting.

.. _non-functional-requirements:

2.2. Non-Functional Requirements
--------------------------------

.. list-table:: Non-Functional Requirements
   :widths: 10 30 15 10 35
   :header-rows: 1

   * - ID
     - Requirement Description
     - Type
     - Priority
     - Justification
   * - NFR01
     - The web interface shall be responsive and accessible on modern web browsers (Chrome, Firefox, Edge).
     - Usability
     - High
     - Ensures a good user experience across common platforms.
   * - NFR02
     - The system should process and analyze a typical IOC within 60 seconds (excluding external API latency).
     - Performance
     - Medium
     - Provides timely results for user queries.
   * - NFR03
     - The article monitoring component should check for new articles at a configurable interval (default: 10 minutes).
     - Performance
     - Medium
     - Balances timeliness with resource usage and API rate limits.
   * - NFR04
     - The system shall be designed modularly to facilitate future enhancements and maintenance.
     - Maintainability
     - High
     - Ensures long-term viability and ease of development.
   * - NFR05
     - API keys and sensitive configurations shall be managed securely (e.g., via environment variables or a .env file).
     - Security
     - High
     - Protects sensitive credentials.
   * - NFR06
     - The system shall handle external API failures gracefully (e.g., retries, error messages) without crashing.
     - Reliability
     - High
     - Ensures system stability when external dependencies are unavailable.
   * - NFR07
     - Code shall be well-documented with comments explaining complex logic.
     - Maintainability
     - Medium
     - Aids understanding and future development.
   * - NFR08
     - The system should be deployable on a standard Linux environment with Python 3.8+ installed.
     - Deployability
     - High
     - Ensures compatibility with common deployment environments.

.. _system-requirements:

2.3. System Requirements
------------------------

*   **Operating System:** Linux (recommended), macOS, Windows (with Python environment).

*   **Python Version:** 3.8 or higher.

*   **Dependencies:** As listed in ``requirements.txt`` (Requests, FastAPI, Uvicorn, Jinja2, Google Generative AI SDK, python-dotenv, stix2, BeautifulSoup, etc.).

*   **External Tools:** ``tshark`` for PCAP analysis (must be in system PATH).

*   **Internet Access:** Required for accessing news sources, ThreatFox API, and Gemini AI API.

*   **API Keys:**

    *   Google Gemini AI API Key.
    *   (No API key explicitly required for ThreatFox public API, but subject to their terms of use).

*   **Hardware (Development/Testing):**

    *   Minimum 2 CPU cores.
    *   Minimum 4GB RAM (8GB recommended for smoother AI interactions and multiple processes).
    *   Minimum 10GB free disk space (for OS, project files, dependencies, and MITRE cache).

.. _user-roles:

2.4. User Roles
---------------

1.  **Cybersecurity Analyst (Primary User):**

    *   Uses the web interface to monitor threats, view analyses, and investigate IOCs.
    *   May use the CLI for quick lookups or specific automation tasks.
    *   Benefits from clear reports and MITRE ATT&CK mapping for understanding threats.

2.  **Incident Responder:**

    *   Uses the tool to quickly gather intelligence on IOCs related to an active incident.
    *   Leverages PCAP analysis feature to check for local presence of threats.

3.  **Threat Intelligence Analyst:**

    *   Uses the tool to gather and contextualize emerging threats from public sources.
    *   May use CLI for scripting bulk IOC lookups or integrating with other tools.

----

.. _system-architecture:

2. System Architecture
======================

.. _overview:

2.1. System Overview
-------------------

The system is built on a modular architecture consisting of several key components:

* CyberMonitor: Core monitoring and IOC detection
* IOCAnalyzer: Threat analysis and enrichment
* Web Interface: User interaction and visualization
* RSS Monitor: Additional threat feed monitoring

.. _components:

2.2. Core Components
-------------------

.. _cyber-monitor:

2.2.1. CyberMonitor
~~~~~~~~~~~~~~~~~~

The CyberMonitor class serves as the primary component for article monitoring and IOC detection. Key features include:

* Real-time article monitoring from NewsNow
* Automated IOC extraction using regex patterns
* Article deduplication and processing
* Integration with IOCAnalyzer for threat analysis

.. _ioc-analyzer:

2.2.2. IOCAnalyzer
~~~~~~~~~~~~~~~~~

The IOCAnalyzer class provides comprehensive threat analysis capabilities:

* Integration with Google's Gemini AI
* ThreatFox API integration for IOC enrichment
* MITRE ATT&CK framework mapping
* HTML report generation

.. _web-interface:

2.2.3. Web Interface
~~~~~~~~~~~~~~~~~~~

The web interface, built with FastAPI, provides:

* Real-time updates via WebSocket
* Interactive IOC analysis
* Article monitoring dashboard
* PCAP file analysis capabilities

----

.. _implementation:

3. Implementation Details
=========================

.. _monitoring:

3.1. Threat Monitoring
---------------------

The system implements sophisticated threat monitoring through:

* Regular article polling from NewsNow
* RSS feed monitoring from ThreatPost
* Real-time IOC detection
* Automated article processing

.. _analysis:

3.2. Threat Analysis
-------------------

Threat analysis is performed through multiple layers:

* Initial IOC detection using regex patterns
* AI-powered analysis using Gemini
* Threat intelligence enrichment via ThreatFox
* MITRE ATT&CK framework mapping

.. _reporting:

3.3. Reporting System
--------------------

The reporting system generates comprehensive threat reports including:

* IOC analysis results
* Threat level assessment
* Recommended actions
* Historical context
* MITRE ATT&CK mappings

----

.. _security:

4. Security Considerations
=========================

.. _data-security:

4.1. Data Security
-----------------

The system implements several security measures:

* Secure API key management
* Environment variable protection
* Safe content processing
* Error handling and logging

.. _privacy:

4.2. Privacy Considerations
--------------------------

Privacy is maintained through:

* Minimal data retention
* Secure data processing
* Controlled information sharing
* Compliance with data protection standards

----

.. _reflection:

5. Project Reflection
=====================

.. _achievements:

5.1. Achievements
----------------

The project successfully achieved:

* Automated threat monitoring
* Real-time IOC analysis
* Comprehensive reporting
* User-friendly interface
* Integration with multiple APIs

.. _challenges:

5.2. Challenges and Solutions
----------------------------

Key challenges encountered and their solutions:

* API rate limiting: Implemented retry mechanisms
* URL resolution: Developed multiple fallback methods
* Real-time updates: Utilized WebSocket technology
* IOC detection: Created sophisticated regex patterns

.. _lessons:

5.3. Lessons Learned
-------------------

Valuable insights gained during development:

* Importance of modular design
* Value of comprehensive error handling
* Benefits of automated testing
* Need for clear documentation

.. _future:

5.4. Future Improvements
-----------------------

Potential enhancements for future development:

* Advanced threat ranking
* Machine learning integration
* Additional data sources
* Enhanced visualization capabilities

----

.. _conclusion:

6. Conclusion
=============

The AI-Powered Cyber Incident Monitoring Tool successfully demonstrates the potential of automated threat monitoring and analysis. By combining multiple technologies and implementing robust security measures, the system provides valuable insights for cybersecurity professionals while maintaining high standards of reliability and usability.

----

.. _references:

7. References
=============

* MITRE ATT&CK Framework Documentation
* ThreatFox API Documentation
* Google Gemini AI Documentation
* FastAPI Documentation
* BeautifulSoup Documentation

----

.. _appendices:

8. Appendices
=============

.. _appendix-a:

8.1. Installation Guide
-----------------------

Detailed instructions for system setup and configuration.

.. _appendix-b:

8.2. API Documentation
---------------------

Comprehensive documentation of system APIs and endpoints.

.. _appendix-c:

8.3. User Guide
--------------

Complete user manual for system operation and maintenance.
