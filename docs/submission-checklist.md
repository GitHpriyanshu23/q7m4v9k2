# Submission checklist

## Build and review

- [x] React frontend and Python FastAPI backend.
- [x] Elexon FUELHH WIND and WINDFOR only.
- [x] January 2026 purchase-decision scope documented.
- [x] Historical publication cutoff enforced.
- [x] Hourly/half-hour alignment explicitly explained.
- [x] Quantitative metrics, coverage, and limitations visible.
- [x] Dockerfile and Compose setup included.
- [x] Automated tests and production frontend build pass.
- [x] README explains structure, startup, methodology, and AI assistance.
- [ ] Candidate has reviewed the code and reproduced the checks.
- [x] Docker image has been built and the container's UI/API checked.

## Public artifacts

- [ ] Create a **public GitHub repository with a random anonymous name**, such as `q7m4v9k2`. Verify name availability; do not imply a repository exists before creation.
- [ ] Push the completed source, data snapshot, tests, docs, and lockfiles. Do not push `.venv`, `.env`, `.vercel`, or credentials.
- [x] Deploy to Vercel or Heroku and verify the Python API on the public deployment, not just the static homepage.
- [x] Add the actual deployment URL to README.
- [ ] Record the customer and technical walkthrough, maximum ten minutes total.
- [ ] Upload the video to YouTube with **Unlisted** visibility.
- [ ] Add the video URL to README.

## Incognito access checks

Open every URL being submitted in an incognito/private window with no account login:

- [ ] Repository opens and source/README are readable.
- [ ] Application opens without login; date/cutoff filters and charts work.
- [ ] `/api/health` returns status `ok` and CSV export downloads.
- [ ] Video plays with sound and both required parts.
- [ ] Every supplied supporting link is accessible to a reviewer.

## Submit

- [ ] Complete the [provided submission form](https://forms.cloud.microsoft/r/FTX6K2bbnU) with the verified repository, deployed app, and unlisted video links.
- [ ] Candidate reviews the final form before sending.
- [ ] Keep the complete assignment effort within the requested 16-hour cap. Record actual effort rather than an invented time log.
