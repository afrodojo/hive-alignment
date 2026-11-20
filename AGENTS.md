# Coding Agent Security Rules

1. **Active Security Review (Cloudflare Skill)**
   Before generating or modifying any code related to authentication, database queries, file uploads, or user input, you MUST review the logic for OWASP Top 10 vulnerabilities (e.g., SQLi, XSS, broken access control).

2. **Secure by Default**
   - NEVER hardcode secrets, API keys, or passwords. Always use environment variables.
   - Always sanitize and validate user input at the boundaries.
   - Default to the principle of least privilege for any IAM roles or database permissions.
