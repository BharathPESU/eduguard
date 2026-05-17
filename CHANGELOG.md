# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Placeholder for YAML-based dynamic rule loading.
- Placeholder for fine-tuned student-specific safety models.

## [1.0.0] - 2026-05-14

### Added
- **Safe Tutor Engine:** Multi-stage guardrail pipeline for Socratic tutoring.
- **Exam Validator:** Automated grading with injection and plagiarism detection.
- **Teacher Dashboard:** Streamlit UI for monitoring violations and submissions.
- **Multi-Provider Support:** Integrated AWS Bedrock and NVIDIA NIM.
- **Observability:** Async MongoDB logging for all interactions and security violations.
- **Guardrails:** Regex-based filters for jailbreaks, academic integrity, and content safety.
- **Docker Support:** Containerized backend and database orchestration.

### Fixed
- Improved JSON extraction from LLM grading responses.
- Resolved circular import issues by keeping `__init__.py` files clean.

### Changed
- Migrated LLM calls to use `any-llm-sdk` abstraction.
- Updated Tutor prompt to be strictly Socratic.
