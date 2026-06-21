# CLAUDE.md — Next.js + SQLite SaaS

Project guidance for Claude Code. Stack: **Next.js (App Router) · TypeScript · SQLite (better-sqlite3 / Drizzle) · Tailwind**.

## Architecture
- `app/` — App Router. Server Components by default; add `"use client"` only when you need state/effects/handlers.
- `app/api/**/route.ts` — route handlers (REST/webhooks). Auth-check at the top of every mutating handler.
- `lib/db.ts` — the single SQLite connection (better-sqlite3 is synchronous; one instance, reused).
- `lib/auth.ts` — session/JWT helpers. `db/schema.ts` — Drizzle schema. `db/migrations/` — generated SQL.
- `components/` — shared UI. `app/(marketing)` vs `app/(app)` route groups split public vs authed.

## Conventions
- TypeScript strict; no `any` — model the type. Validate all external input with **zod** at the boundary.
- Data access goes through `lib/` query functions, never inline SQL in components/handlers.
- Server Actions for mutations from forms; route handlers for external/API/webhook callers.
- Money in integer minor units (cents). Timestamps UTC ISO-8601. IDs: `crypto.randomUUID()` or cuid2.
- Tailwind utilities in JSX; extract a component before a `className` grows past ~6 utilities.

## SQLite specifics
- `better-sqlite3` is **synchronous** — do NOT `await` queries; wrap multi-statement writes in `db.transaction()`.
- Enable `PRAGMA journal_mode = WAL;` and `PRAGMA foreign_keys = ON;` once at startup (`lib/db.ts`).
- One connection per process. On serverless, prefer a persistent volume or Turso/libSQL — local SQLite resets on cold start.
- Migrations: `drizzle-kit generate` → commit the SQL → apply on boot. Never hand-edit applied migrations.

## Commands
```bash
pnpm dev            # next dev
pnpm build && pnpm start
pnpm test           # vitest
pnpm db:generate    # drizzle-kit generate
pnpm db:migrate     # apply migrations
pnpm lint && pnpm typecheck
```

## Definition of done
- `pnpm typecheck` + `pnpm lint` clean; new logic has a vitest test.
- Every API/Server Action: authenticated, zod-validated, errors return a typed shape (no leaked stack traces).
- No secrets in client components or `NEXT_PUBLIC_*`. DB writes are transactional. Loading + error UI exist.

## Guardrails
- Never commit `.env*`, `*.db`, or `db/*.sqlite`. Never run destructive SQL (`DROP`/`DELETE` w/o `WHERE`) outside a migration.
- Don't introduce an ORM-bypassing raw query without a `lib/` wrapper + test.
- Ask before adding a dependency that overlaps something already in the stack.
