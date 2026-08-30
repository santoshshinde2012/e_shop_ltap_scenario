# Security

This project is a small, self-contained demo. It ships synthetic CSV data, runs entirely locally,
makes no network calls, has no runtime dependencies beyond the standard library, and stores no
secrets or credentials.

If you believe you have found a security issue — in a development dependency, or in how the package
handles file paths passed through `--data-dir` — please **do not open a public issue**. Use GitHub's
private vulnerability reporting on this repository ("Security" tab → "Report a vulnerability"), or
contact the maintainer through the GitHub profile. You will get an acknowledgement within a few days.

Development dependencies are kept current by Dependabot (`.github/dependabot.yml`).
