# Mermaid Diagram Guide

Quick reference for Mermaid syntax used in diagram generation.

## Flowchart

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

### Node Shapes
- `[Rectangle]` - Process
- `(Rounded]` - Rounded rectangle
- `((Circle))` - Circle
- `[Diamond]` - Decision
- `[[Subroutine]]` - Subroutine
- `[(Cylinder)]` - Database

### Arrow Types
- `-->` - Arrow
- `---` - Line
- `-.->` - Dotted arrow
- `==>` - Thick arrow

## Sequence Diagram

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Message
    B-->>A: Response
    A->>B: Another message
```

## Class Diagram

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +bark()
    }
    Animal <|-- Dog
```

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Start
    Processing --> Complete: Done
    Processing --> Error: Fail
    Error --> Idle: Retry
    Complete --> [*]
```

## Entity Relationship

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    PRODUCT ||--o{ LINE-ITEM : "is in"
}
```

## Common Patterns

### Horizontal Flow
```mermaid
graph LR
    A[Input] --> B[Process] --> C[Output]
```

### Vertical Flow
```mermaid
graph TB
    A[Top] --> B[Middle] --> C[Bottom]
```

### Subgraph (Grouping)
```mermaid
graph TB
    subgraph Group1
        A --> B
    end
    subgraph Group2
        C --> D
    end
    B --> D
```

## Export Options

### VS Code Extension
Install "Markdown Preview Mermaid Support" or "Mermaid Markdown Syntax Highlighting"

### CLI Tools
- `@mermaid-js/mermaid-cli` - Command line rendering
- `mermaid-cli` - Standalone CLI

### Online Editors
- https://mermaid.live - Live Mermaid editor
- https://knsv.github.io/mermaid/ - Official demos
