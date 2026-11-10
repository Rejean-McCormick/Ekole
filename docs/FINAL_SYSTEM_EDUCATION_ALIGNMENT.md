# Final-system learning engine and publication boundary — Ékole Core

**Scope:** `FC-11` with support to `FC-10`; neutral, locally operable educational engine. `Ekole-Pastorale` and `ekole-quebec` are **independent content repositories**; no religious curriculum or Orgo state is embedded as mandatory engine logic.

## Content pack and teacher preview

- Ekole Core imports `ekole.content-pack/0.1` from an explicitly selected content directory. Its pack manifest and course/file references are owner-qualified locally; this does not grant student/public release permission.
- The teacher-only synthetic preview `ekole.tandem-teacher-preview/1.0` remains disabled by default, accessible only through the local authenticated editor, and has no Orgo runtime effect.
- When a derived `publications/eleve/<course>.json` explicitly has `publication_autorisee=false` or `publication_eleve=false`, the unauthenticated learner endpoint **returns a safe preparation stub with no modules**. It must not expose a source's teaching text merely because the file exists. Authorized reviewer access remains a separate teacher-side mechanism.
- Actual course release workflow, identity/consent and institution-specific publication remain owner decisions; a file status alone is never a trusted network authorization token.

## Tests and offline limitations

Run `python -m unittest discover -s tests -v`. Tests requiring the separate `ekole-quebec` content checkout now **skip explicitly if its source pack is absent**, rather than reporting an engine failure; those integrations remain unqualified until its owner archive is supplied. Core and supplied pastoral fixtures are exercised independently. The branch runner proves an explicit unapproved pastoral lesson is not exposed through the local learner interface.

An integration to UCKK/Moodle is **not implemented by this change**; see UCKK's read-only source inspector and the cross-owner handoff document.
