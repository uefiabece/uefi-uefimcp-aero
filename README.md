# uefi-uefimcp — MCP Template for UFABC Subjects

This repository is the **base template** for all UEFIabc MCP (Model Context Protocol) servers.

Each MCP server in this ecosystem is specialized for a specific UFABC course or subject, loaded with educational content such as syllabi, bibliographies, past exams, exercises, and media. The goal is for each server to be a genuine expert in its domain: capable of teaching, explaining, solving exercises, and reasoning practically about subject matter.

---

## Ecosystem Hierarchy

```
uefi-uefimcp           ← this repo (generic template)
  └── uefi-<course>    ← course-level repo (e.g. uefi-science-and-technology)
        └── uefi-<subject>  ← subject-level repo (e.g. uefi-precalculus)
```

When creating a new subject MCP, fork or copy this template, then specialize it by:
1. Filling `/content/` with subject-specific material
2. Editing `/config/subject.json` with subject metadata
3. Updating the system prompt in `/prompts/system.md`
4. Adding or removing tools in `/src/tools/` as needed

---

## Directory Structure

```
uefi-uefimcp/
├── src/
│   ├── server.py           # MCP server entry point
│   ├── tools/              # MCP tool implementations
│   │   ├── content.py      # Syllabus, bibliography, exam retrieval
│   │   ├── teaching.py     # Concept explanation, teaching flows
│   │   └── exercises.py    # Exercise solving and generation
│   ├── resources/
│   │   └── loader.py       # Content loading and indexing utilities
│   └── prompts/
│       └── templates.py    # Prompt template helpers
├── content/
│   ├── syllabus/           # Official course syllabus files
│   ├── bibliography/       # Reading materials and references
│   ├── exams/              # Past exams and answer keys
│   ├── exercises/          # Practice exercises (by topic)
│   ├── notes/              # Lecture notes and summaries
│   └── media/              # Images, diagrams, circuit files, etc.
├── prompts/
│   ├── system.md           # Base system prompt — defines the server's identity
│   ├── teaching.md         # Prompt fragment for teaching mode
│   └── solver.md           # Prompt fragment for exercise-solving mode
├── config/
│   └── subject.json        # Subject metadata and feature flags
└── docs/
    ├── setup.md            # How to run the MCP server
    ├── content-guide.md    # How to add and structure content
    └── customization.md    # How to specialize this template
```

---

## Capabilities (all subjects)

- **Teach** concepts from the subject syllabus with clear, structured explanations
- **Retrieve** syllabus, bibliography, and official course materials
- **Solve** exercises step-by-step, showing reasoning
- **Generate** new exercises at configurable difficulty levels
- **Reference** past exams and explain solutions
- **Search** across all loaded content

## Capabilities (subject-specific, enabled via config)

- **Interpret images** (e.g. circuit diagrams, graphs, chemical structures)
- **Create or edit structured files** (e.g. circuit netlists, data tables)
- **Run computations** (symbolic math, numerical simulation)

---

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the MCP server (stdio transport, for use with Claude Desktop / Claude Code)
python -m src.server
```

See [`docs/setup.md`](./docs/setup.md) for full setup instructions.
