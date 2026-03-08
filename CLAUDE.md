# CLAUDE.md

This file contains instructions for working with this Agentic Coding vault.

## Documentation Workflow

This vault was created using a **Map-Reduce documentation pipeline** to generate comprehensive documentation from a GitHub repository. Here's how it works:

### Overview

The workflow has **5 steps** that transform raw research into a polished, interconnected Obsidian vault:

```
GitHub Repo → Parallel Research → Concept Extraction → Global Synthesis → Refinement → Final Assembly
```

### Step-by-Step Process

#### Step 1: Parallel Research (Drafting)
- Use `technical-docs-subagent` to research the target repository
- Divide into **5 research groups** (can be customized):
  - Group A: Core architecture (src/, apps/, docs/)
  - Group B: Agent system (.agents/, .agent/workflows/)
  - Group C: Extensions/skills (extensions/, skills/)
  - Group D: UI layer (ui/, packages/)
  - Group E: Evolution/history (CHANGELOG.md, VISION.md, etc.)
- Output: 8 raw markdown files in `raw_docs/`

#### Step 2: Concept Extraction (Map Phase)
- Use `concept-extraction-agent` to process each raw markdown file
- Extract structured JSON manifests with:
  - Primary concepts (concepts the section "owns")
  - Referenced concepts (concepts defined elsewhere)
  - Key terminology
- Output: JSON manifests in `raw_docs/manifests/`

#### Step 3: Global Synthesis (Reduce Phase)
- Use `doc-synthesis-orchestrator` to analyze all manifests
- Resolve conflicts (determine which section "owns" each concept)
- Generate two outputs:
  - `global_glossary.json` - Canonical terminology mapping
  - `concept_map.md` - Cross-reference index
- Output: Glossary + Concept Map

#### Step 4: Refinement (Editing Phase)
- Use `final-technical-editor` to polish each raw markdown file
- Apply rules:
  - Standardize terminology against glossary
  - Add cross-references (e.g., `[See Section X: Title]`)
  - Remove redundant deep-dives (reference owning section instead)
- Output: Refined files in `refined_docs/`

#### Step 5: Final Assembly
- Concatenate all refined files in order
- Append the Concept Map
- Move to final location
- For Obsidian: Create separate .md files with wikilinks

### Customization for Other Projects

Adjust these parameters based on your target:

| Parameter | Example Value |
|-----------|---------------|
| **Target Repository** | https://github.com/owner/repo |
| **Research Groups** | Divide by module/type |
| **Output Sections** | 6-10 sections recommended |
| **Output Format** | Obsidian wikilinks or standard markdown |

### Example Prompt for New Project

```
## Task: Generate Documentation for [PROJECT_NAME]

Use the Map-Reduce pipeline:

### Step 1: Research
Research [REPO_URL] and generate [N] sections:
- Section 1: [Topic]
- Section 2: [Topic]
...

Output raw markdown files to `raw_docs/`

### Step 2: Extract Concepts
Process each file with concept-extraction-agent to generate JSON manifests.

### Step 3: Synthesize
Use doc-synthesis-orchestrator to create:
- Global glossary
- Concept map

### Step 4: Refine
Polish with final-technical-editor using glossary rules.

### Step 5: Assemble
Create final documentation with proper cross-references.
```

## Obsidian Structure

This vault follows Obsidian best practices:

- **Index.md** - Main entry point per project
- **Wikilinks** - `[[filename]]` for internal links
- **Concept Map** - Cross-reference index for finding concepts
- **Numbered sections** - For logical ordering (01_, 02_, etc.)

## Notes

- The pipeline works best with well-documented, modular repositories
- Concept ownership conflicts are resolved by designating one section as the "owner"
- Cross-references help readers navigate between related topics
