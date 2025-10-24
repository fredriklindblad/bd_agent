# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-10-24

### Added
- Initial release of **BD Agent**: an AI-powered stock analysis and screening tool integrating Börsdata API, OpenAI, and PydanticAI.  
- Basic screening capabilities: filter by country, sector and industry.  
- Company analysis agent: fetch key financial data, propose relevant KPI’s, and return narrative rationale.  
- Portfolio summary module: accept list of ticker symbols and provide aggregated risk/return overview.  
- Streamlit user interface: interactive web UI for entering natural-language prompts and displaying results.  
- CLI interface (Typer based): command-line support for screening and analysis workflows.  
- Intent classifier: routes user natural-language queries to appropriate agent (screening vs. analysis vs. portfolio).  
- Evaluation framework: golden set for intent classification, plus test harness for measuring accuracy/F1.  
- Env-variable configuration: support for `OPENAI_API_KEY` and `BORSDATA_API_KEY`.  
- Documentation: this README.md + basic project structure overview.

### Changed
*(none — this is the first official release)*

### Fixed
*(none — initial release)*

### Removed
*(none — initial release)*

---

## [Unreleased]
*(Prepare for next release — e.g., enhancements, new features, bug-fixes)*
