# ATLAS Personal Research & Venture Hub

## Purpose

Create a user-centered research operating system where personal identity, projects, creative work, organizations, ventures and long-term ideas become structured research domains inside ATLAS.

## Principle

The user is not a passive profile. Their projects form a living knowledge graph.

ATLAS should be able to:
- understand each project and its history;
- relate projects to one another;
- identify opportunities, risks and missing capabilities;
- generate research agendas;
- track decisions and outcomes;
- preserve creative identity;
- propose experiments and improvements;
- surface relevant external developments;
- move useful knowledge between projects without contaminating context.

## Personal domains

Examples:
- music and composition;
- writing and publishing;
- audiovisual and performance;
- Instituto/social impact;
- A+ ventures;
- architecture/real estate;
- education/children's projects;
- technology and AI;
- research and frontier science.

Each domain gets:
- canonical identity;
- goals;
- assets;
- current state;
- opportunities;
- risks;
- open questions;
- research backlog;
- relevant ministries;
- context capsule;
- history and decisions.

## Project Knowledge Graph

Nodes:
- person
- project
- company/organization
- work
- product
- asset
- opportunity
- hypothesis
- partner
- market
- document
- decision
- experiment

Edges:
- owns
- created
- depends_on
- relates_to
- competes_with
- can_enable
- originated_from
- validated_by
- contradicts
- inspired_by
- transferable_to

## Cross-project research

ATLAS should actively look for:
- capabilities reusable across projects;
- content that can become products;
- IP that can migrate between media;
- financing/funding opportunities;
- technology leverage;
- audience overlap;
- institutional partnerships;
- data or knowledge gaps;
- experiments that benefit multiple projects.

## ChatGPT connection

ATLAS should expose a governed MCP/API surface so ChatGPT can:
- read project context;
- search ATLAS memory;
- add approved notes/hypotheses;
- update project state;
- create research missions;
- inspect ministry outputs;
- push validated discoveries to the ATLAS knowledge graph.

The mobile app and ChatGPT become two clients of the same ATLAS backend.

## GitHub synchronization

Code, architecture and formal research artifacts belong in GitHub.
Personal/private operational data should not be committed to a public repository by default.

Recommended split:
- public repo: code, schemas, generic methodology, tests, docs;
- private backend/database: personal profile, project state, private notes, credentials;
- optional private repo: sensitive research artifacts requiring version control.

## Continuous improvement loop

conversation -> structured observation -> project/domain routing -> ministry research -> validation -> knowledge graph -> opportunity detection -> user briefing -> action/experiment -> outcome -> learning

## User interface

Suggested app section: **My World**

Views:
- Me
- Projects
- Ideas
- Opportunities
- Research
- Creative Library
- Organizations
- Decisions
- Timeline
- Connections

## Privacy rule

Never treat the public GitHub repository as the user's personal memory store. Personal context needs explicit privacy boundaries, encryption and export/delete controls.
