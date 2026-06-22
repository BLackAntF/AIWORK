---
name: diagram-generator
description: "Generate Visio-style diagrams using Node.js (mermaid, plantuml). Creates flowcharts, architecture diagrams, UML diagrams, and data flow charts for software engineering documents. Use when user needs professional diagrams in documents."
---

# Diagram Generator

Generate professional Visio-style diagrams for software engineering documents using Node.js libraries.

## Overview

Creates flowcharts, architecture diagrams, UML diagrams, and data flow charts that can be embedded in documentation.

## Supported Diagram Types

1. **Flowcharts** - Process flows, decision trees
2. **Architecture Diagrams** - System components, layers
3. **UML Diagrams** - Class diagrams, sequence diagrams
4. **Data Flow Diagrams** - DFD, ER diagrams
5. **Sequence Diagrams** - Interaction flows
6. **State Diagrams** - State machines

## Workflow

1. **Identify diagram type** - Determine best visualization
2. **Generate diagram code** - Create Mermaid/PlantUML syntax
3. **Render to image** - Convert to PNG/SVG
4. **Embed in document** - Reference generated image

## Output Formats

- PNG (high resolution)
- SVG (scalable)
- PDF (print quality)

## Diagram Code Examples

### Flowchart (Mermaid)

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

### Sequence Diagram (Mermaid)

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant D as Database
    U->>A: Request
    A->>D: Query
    D-->>A: Result
    A-->>U: Response
```

### Architecture (Mermaid)

```mermaid
graph TB
    subgraph Frontend
        W[Web App]
        M[Mobile App]
    end
    subgraph Backend
        API[API Gateway]
        S1[Service 1]
        S2[Service 2]
    end
    subgraph Data
        DB[(Database)]
        C[Cache]
    end
    W --> API
    M --> API
    API --> S1
    API --> S2
    S1 --> DB
    S2 --> DB
    S1 --> C
```

## Resources

### scripts/

- `render-diagram.js` - Render Mermaid/PlantUML to image
- `mermaid-to-png.js` - Convert Mermaid to PNG
