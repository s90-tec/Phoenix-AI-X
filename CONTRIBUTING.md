# Contributing to Phoenix AI X

Thank you for improving Phoenix AI X. Open an issue before proposing material architecture changes.

1. Create a focused branch and keep commits coherent.
2. Preserve Clean Architecture: domain code cannot import infrastructure or presentation code.
3. Add typed, documented code and appropriate tests under the relevant test tier.
4. Run `pre-commit run --all-files` and `pytest` before opening a pull request.
5. Describe design decisions, operational impact, and any migration or security implications.

Never commit credentials, datasets with restricted licenses, model artifacts, or production trading configuration.

