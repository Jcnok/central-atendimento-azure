---
description: Fix Online Support for Anonymous Users
---
# Fix Online Support for Anonymous Users

## Problem
- The "Atendimento Online" (Home.jsx) chat widget does not handle anonymous users well.
- It asks for "Client ID" for invoices instead of email.
- It gives generic troubleshooting for "no internet" without identifying the user for specific checks.
- Markdown rendering is missing in the chat widget.

## Solution
1.  **Frontend (`Home.jsx`)**:
    - Import `ReactMarkdown`.
    - Render bot messages using `<ReactMarkdown>`.

2.  **Backend Agents**:
    - **FinancialAgent**: Update prompt to check for `client_email` in context. If missing (anonymous), explicitly ask the user for their email to retrieve invoices.
    - **TechnicalAgent**: Update prompt to check for `client_id` in context. If missing, ask for email/identification before creating tickets or running specific checks.
    - **Orchestrator**: Inject `is_authenticated` flag into context (optional, but good for logic).

## Verification
- **Markdown**: Check `Home.jsx` code.
- **Financial**: Verify `FinancialAgent` prompt instructs to ask for email if anonymous.
- **Technical**: Verify `TechnicalAgent` prompt instructs to ask for ID/email if anonymous.
- **Tests**: Run existing agent tests to ensure no regression.
