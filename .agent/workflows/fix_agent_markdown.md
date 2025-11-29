---
description: Fix Markdown Rendering in Agent CRM
---
# Fix Markdown Rendering in Agent CRM

## Problem
The "Agente Ia - CRM" (Agent.jsx) displays responses as plain text, making formatted information (lists, tables, bold text) difficult to read and confusing.

## Solution
- Import `react-markdown` in `frontend/src/pages/Agent.jsx`.
- Replace the plain text rendering of `msg.content` with `<ReactMarkdown>{msg.content}</ReactMarkdown>` for agent messages.

## Verification
- Check `Agent.jsx` code to ensure `ReactMarkdown` is imported and used.
- (Implicit) The user should see formatted text in the Agent CRM interface.
