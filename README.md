# Homework Converter

AI-assisted PDF worksheet accommodation tool. The teacher uploads a PDF, the backend analyzes every page with OpenAI, rebuilds the questions with readable layout, then runs an AI quality review.

**Status:** Prototype. Do not use with identifiable student information before school approval, privacy review, and testing on representative worksheets.

## Deploy

1. Deploy the `backend/` folder as a Python web service (Render or equivalent). Set `OPENAI_API_KEY` as a secret and `ALLOWED_ORIGINS=https://ckormylo.github.io`.
2. Publish `frontend/` using GitHub Pages (Settings → Pages → GitHub Actions); configure the backend URL in `frontend/app.js`.
3. Upload a non-identifying worksheet and review each generated PDF against its original.

Default visual accommodations: three problems per page, 18 pt text, generous line spacing, simple cream background, meaningful highlight spans. Simplification is optional and needs teacher review. Content preservation is prioritized over appearance.
