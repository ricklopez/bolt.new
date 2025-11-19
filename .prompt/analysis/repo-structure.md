# Repository Structure Analysis: bolt.new

**Analysis Date:** 2025-11-18
**Repository:** bolt.new - AI-powered full-stack web development IDE in the browser

---

## 1. File Classification by Language

### File Count by Type
- **TypeScript/TSX files**: ~96 total
  - `.ts` files: ~65
  - `.tsx` files: ~31
- **JavaScript files**: 0 (pure TypeScript project)
- **SCSS files**: 12
- **JSON files**: 2 (package.json, tsconfig.json)
- **Markdown files**: 2 (README.md, CONTRIBUTING.md)
- **TOML files**: 1 (wrangler.toml)
- **SVG files**: 6 (icons and logos)
- **YAML files**: 3 (GitHub workflows and config)
- **Shell scripts**: 1 (bindings.sh)
- **Config files**: Multiple (eslint, prettier, editorconfig, vite, uno)

### Language Distribution
- **Primary Language**: TypeScript (100% of application code)
- **Styling**: SCSS/CSS
- **Markup**: HTML (embedded in TSX), Markdown
- **Configuration**: JSON, TOML, YAML
- **Deployment**: Cloudflare Workers/Pages configuration

---

## 2. Directory Architecture

### Root Level Structure
```
/home/user/bolt.new/
├── .github/              # GitHub Actions workflows and issue templates
├── .husky/               # Git hooks
├── .prompt/              # DotPrompt workspace (IR templates for AI analysis)
├── app/                  # Main application source code
├── functions/            # Cloudflare Workers functions
├── icons/                # Custom SVG icons
├── public/               # Static assets
├── types/                # Global TypeScript type definitions
└── [config files]        # Various configuration files
```

### Detailed App Directory Structure

```
app/
├── components/           # React components
│   ├── chat/            # Chat interface components
│   ├── editor/          # Code editor (CodeMirror integration)
│   ├── header/          # App header components
│   ├── sidebar/         # Sidebar with chat history
│   ├── ui/              # Reusable UI components
│   └── workbench/       # IDE-like workbench components
├── lib/                 # Core application logic
│   ├── .server/         # Server-side code (LLM integration)
│   ├── hooks/           # React hooks
│   ├── persistence/     # IndexedDB persistence layer
│   ├── runtime/         # Action runner and message parser
│   ├── stores/          # State management (Nanostores)
│   └── webcontainer/    # WebContainer API integration
├── routes/              # Remix routes (pages and API endpoints)
├── styles/              # Global SCSS styles
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
├── entry.client.tsx     # Client-side entry point
├── entry.server.tsx     # Server-side entry point
└── root.tsx             # Root layout component
```

### Purpose of Major Directories

| Directory | Purpose |
|-----------|---------|
| `.prompt/` | DotPrompt workspace with IR templates for codebase analysis |
| `app/lib/.server/llm/` | Server-side LLM integration (Anthropic Claude API) |
| `app/lib/runtime/` | Core runtime logic for parsing AI messages and executing actions |
| `app/lib/stores/` | Client-side state management using Nanostores |
| `app/lib/webcontainer/` | Integration with StackBlitz WebContainer API |
| `app/components/` | React components organized by feature |
| `functions/` | Cloudflare Workers edge functions |
| `public/` | Static assets (images, favicon) |

---

## 3. Frameworks Detected

### Frontend Frameworks & Libraries

**Core Framework:**
- **Remix Run** (v2.10.2) - Full-stack React framework
- **React** (v18.2.0) - UI library
- **React DOM** (v18.2.0)

**Styling & UI:**
- **UnoCSS** (v0.61.3) - Atomic CSS framework
- **SCSS** - CSS preprocessor
- **Framer Motion** (v11.2.12) - Animation library
- **React Toastify** (v10.0.5) - Toast notifications
- **Radix UI** - Headless UI components (Dialog, Dropdown Menu)
- **React Resizable Panels** (v2.0.20) - Resizable panel layout

**Code Editor:**
- **CodeMirror 6** - Complete code editor integration
  - Multiple language packages (JavaScript, Python, CSS, HTML, JSON, Markdown, etc.)
  - VSCode theme (v4.23.0)
  - Search, autocomplete, and command support

**Terminal:**
- **XTerm.js** (v5.5.0) - Terminal emulator with addons

**Markdown:**
- **React Markdown** (v9.0.1)
- **Remark GFM** (v4.0.0) - GitHub Flavored Markdown
- **Rehype Raw** (v7.0.0)
- **Rehype Sanitize** (v6.0.0)
- **Shiki** (v1.9.1) - Syntax highlighting

### Backend/Runtime

**Deployment Platform:**
- **Cloudflare Pages** - Static site hosting
- **Cloudflare Workers** - Edge computing
- **Wrangler** (v3.63.2) - Cloudflare CLI

**WebContainer:**
- **@webcontainer/api** (v1.3.0-internal.10) - In-browser Node.js runtime

**AI/LLM Integration:**
- **AI SDK** (v3.3.4) - Vercel AI SDK
- **@ai-sdk/anthropic** (v0.0.39) - Anthropic provider
- **Claude 3.5 Sonnet** - LLM model

### State Management
- **Nanostores** (v0.10.3) - Lightweight state manager
- **@nanostores/react** (v0.7.2) - React bindings

### Build Tools
- **Vite** (v5.3.1) - Build tool and dev server
- **TypeScript** (v5.5.2) - Type system
- **pnpm** (v9.4.0) - Package manager
- **Vitest** (v2.0.1) - Testing framework

**Vite Plugins:**
- vite-plugin-node-polyfills
- vite-plugin-optimize-css-modules
- vite-tsconfig-paths

### Development Tools
- **ESLint** - Linting
- **Prettier** (v3.3.2) - Code formatting
- **Husky** - Git hooks
- **Zod** (v3.23.8) - Schema validation

---

## 4. Backend / Frontend / Shared Boundaries

### BACKEND CODE

**Location:** `/app/lib/.server/` and `/functions/`

#### Server-Side Components:

**1. LLM Integration** (`/app/lib/.server/llm/`)
- `app/lib/.server/llm/stream-text.ts` - AI streaming handler
- `app/lib/.server/llm/prompts.ts` - System prompts for Claude
- `app/lib/.server/llm/model.ts` - Anthropic model configuration
- `app/lib/.server/llm/constants.ts` - LLM constants (max tokens)
- `app/lib/.server/llm/api-key.ts` - API key management
- `app/lib/.server/llm/switchable-stream.ts` - Stream switching logic

**2. API Routes** (`/app/routes/`)
- `app/routes/api.chat.ts` - Chat API endpoint (POST /api/chat)
- `app/routes/api.enhancer.ts` - Prompt enhancement endpoint (POST /api/enhancer)

**3. Cloudflare Workers** (`/functions/`)
- `functions/[[path]].ts` - Catch-all function handler

**Key Backend Features:**
- Anthropic Claude API integration
- Streaming text responses with continuation support
- Environment variable management
- Server-side rendering (SSR) via Remix

### FRONTEND CODE

**Location:** `/app/components/`, `/app/routes/` (client components)

#### UI Components:

**1. Chat Interface** (`/app/components/chat/`)
- `app/components/chat/Chat.client.tsx` - Main chat component
- `app/components/chat/BaseChat.tsx` - Base chat layout
- `app/components/chat/Messages.client.tsx` - Message list
- `app/components/chat/AssistantMessage.tsx` - AI messages
- `app/components/chat/UserMessage.tsx` - User messages
- `app/components/chat/Artifact.tsx` - Code artifacts display
- `app/components/chat/Markdown.tsx` - Markdown rendering
- `app/components/chat/CodeBlock.tsx` - Code block display
- `app/components/chat/SendButton.client.tsx` - Send button

**2. Workbench** (`/app/components/workbench/`)
- `app/components/workbench/Workbench.client.tsx` - Main workbench
- `app/components/workbench/EditorPanel.tsx` - Code editor panel
- `app/components/workbench/Preview.tsx` - Live preview
- `app/components/workbench/FileTree.tsx` - File explorer
- `app/components/workbench/Terminal.tsx` - Terminal component
- `app/components/workbench/FileBreadcrumb.tsx` - File navigation
- `app/components/workbench/PortDropdown.tsx` - Port selector

**3. Editor** (`/app/components/editor/codemirror/`)
- `app/components/editor/codemirror/CodeMirrorEditor.tsx` - Editor component
- `app/components/editor/codemirror/languages.ts` - Language support
- `app/components/editor/codemirror/cm-theme.ts` - Editor theme
- `app/components/editor/codemirror/indent.ts` - Indentation logic
- `app/components/editor/codemirror/BinaryContent.tsx` - Binary file display

**4. UI Components** (`/app/components/ui/`)
- Dialog, IconButton, Slider, ThemeSwitch, PanelHeader, LoadingDots

**5. Sidebar & Header**
- `app/components/sidebar/Menu.client.tsx` - Sidebar menu
- `app/components/sidebar/HistoryItem.tsx` - Chat history items
- `app/components/header/Header.tsx` - App header

### SHARED CODE

**Location:** `/app/lib/` (non-.server), `/app/types/`, `/app/utils/`

#### State Management (`/app/lib/stores/`)
- `app/lib/stores/workbench.ts` - Workbench state (orchestrates entire IDE)
- `app/lib/stores/chat.ts` - Chat state
- `app/lib/stores/files.ts` - File system state
- `app/lib/stores/editor.ts` - Editor state
- `app/lib/stores/terminal.ts` - Terminal state
- `app/lib/stores/previews.ts` - Preview state
- `app/lib/stores/settings.ts` - App settings
- `app/lib/stores/theme.ts` - Theme state

#### Runtime Logic (`/app/lib/runtime/`)
- `app/lib/runtime/message-parser.ts` - Parse AI artifact messages
- `app/lib/runtime/action-runner.ts` - Execute file/shell actions
- `app/lib/runtime/message-parser.spec.ts` - Unit tests

#### WebContainer Integration
- `app/lib/webcontainer/index.ts` - WebContainer initialization
- `app/lib/webcontainer/auth.client.ts` - Authentication

#### Persistence (`/app/lib/persistence/`)
- `app/lib/persistence/db.ts` - IndexedDB operations
- `app/lib/persistence/useChatHistory.ts` - Chat history hook

#### Types (`/app/types/`)
- `app/types/actions.ts` - Action types (FileAction, ShellAction)
- `app/types/artifact.ts` - Artifact data types
- `app/types/terminal.ts` - Terminal types
- `app/types/theme.ts` - Theme types

#### Utilities (`/app/utils/`)
- Buffer operations, class names, constants, debounce
- Diff computation, logging, markdown parsing
- Mobile detection, promises, terminal utils
- Shell command parsing, text stripping

---

## 5. Domain Models and Business Logic

### Core Domain Entities

#### 1. Artifact (`app/types/artifact.ts`)
```typescript
interface BoltArtifactData {
  id: string;
  title: string;
}

// Extended state in app/lib/stores/workbench.ts
interface ArtifactState {
  id: string;
  title: string;
  closed: boolean;
  runner: ActionRunner;
}
```
**Purpose:** Represents a complete project/task generated by AI containing files and shell commands.

#### 2. Actions (`app/types/actions.ts`)
```typescript
type ActionType = 'file' | 'shell';

interface FileAction extends BaseAction {
  type: 'file';
  filePath: string;
  content: string;
}

interface ShellAction extends BaseAction {
  type: 'shell';
  content: string;
}

type BoltAction = FileAction | ShellAction;

// Action state in app/lib/runtime/action-runner.ts
type ActionStatus = 'pending' | 'running' | 'complete' | 'aborted' | 'failed';

interface ActionState {
  status: ActionStatus;
  abort: () => void;
  executed: boolean;
  abortSignal: AbortSignal;
  error?: string;
}
```
**Purpose:** Represents individual operations (file creation/modification or shell command execution) within an artifact.

#### 3. File System (`app/lib/stores/files.ts`)
```typescript
interface File {
  type: 'file';
  content: string;
  isBinary: boolean;
}

interface Folder {
  type: 'folder';
}

type Dirent = File | Folder;
type FileMap = Record<string, Dirent | undefined>;
```
**Purpose:** Represents the in-browser file system state synchronized with WebContainer.

#### 4. Chat History (`app/lib/persistence/useChatHistory.ts`)
```typescript
interface ChatHistoryItem {
  id: string;
  urlId?: string;
  description?: string;
  messages: Message[];
  timestamp: string;
}
```
**Purpose:** Persisted chat conversations stored in IndexedDB.

#### 5. Editor Document (`app/components/editor/codemirror/CodeMirrorEditor.tsx`)
```typescript
interface EditorDocument {
  filePath: string;
  value: string;
  scroll?: ScrollPosition;
}
```
**Purpose:** Represents an open file in the code editor.

### Business Logic Components

#### 1. Message Parser (`app/lib/runtime/message-parser.ts`)
**Core Class:** `StreamingMessageParser`

**Purpose:** Parses streaming AI responses to extract artifact and action tags.

**Key Methods:**
- `parse(messageId, input)` - Parse streaming text
- `#parseActionTag()` - Extract action attributes
- `#extractAttribute()` - Parse XML-like attributes

**Tags Parsed:**
- `<boltArtifact>` - Container for project
- `<boltAction type="file" filePath="...">` - File operation
- `<boltAction type="shell">` - Shell command

#### 2. Action Runner (`app/lib/runtime/action-runner.ts`)
**Core Class:** `ActionRunner`

**Purpose:** Executes actions (file writes, shell commands) in WebContainer.

**Key Methods:**
- `addAction(data)` - Queue an action
- `runAction(data)` - Execute action sequentially
- `#executeAction(actionId)` - Run single action
- `#runShellAction(action)` - Execute shell command
- `#runFileAction(action)` - Write file to WebContainer

**Execution Model:** Sequential execution with abort support.

#### 3. Workbench Store (`app/lib/stores/workbench.ts`)
**Core Class:** `WorkbenchStore`

**Purpose:** Orchestrates the entire IDE experience.

**Managed Stores:**
- PreviewsStore - Live preview management
- FilesStore - File system state
- EditorStore - Open documents
- TerminalStore - Terminal state

**Key Operations:**
- File save/reset/modification tracking
- Artifact lifecycle management
- Action orchestration
- Document management

#### 4. Files Store (`app/lib/stores/files.ts`)
**Core Class:** `FilesStore`

**Purpose:** Syncs WebContainer file system with app state.

**Key Features:**
- Real-time file watching via WebContainer API
- Binary file detection
- File modification tracking
- Diff computation

**Event Handling:**
- `add_dir`, `remove_dir` - Directory changes
- `add_file`, `change` - File changes
- `remove_file` - File deletion

#### 5. System Prompt (`app/lib/.server/llm/prompts.ts`)
**Function:** `getSystemPrompt(cwd: string)`

**Purpose:** Generates comprehensive system prompt for Claude AI.

**Includes:**
- WebContainer environment constraints
- Artifact generation rules
- File modification handling
- Code formatting guidelines
- Action tag specifications

**Key Constraints:**
- No pip support (Python stdlib only)
- No native binaries
- No Git
- Prefer Vite for web servers
- Use Node.js scripts over shell scripts

---

## 6. API Endpoints

### Remix Routes (HTTP Endpoints)

#### 1. Chat API
**File:** `app/routes/api.chat.ts`
**Endpoint:** `POST /api/chat`
**Handler:** `chatAction()`

**Input:**
```typescript
{
  messages: Messages  // Array of user/assistant messages
}
```

**Output:** Streaming text response

**Features:**
- Streams AI responses using Vercel AI SDK
- Automatic continuation when max tokens reached (8192)
- Max 2 continuation segments
- Uses SwitchableStream for seamless continuation

**Dependencies:**
- `streamText()` from LLM module
- Anthropic Claude 3.5 Sonnet
- System prompt injection

#### 2. Prompt Enhancer API
**File:** `app/routes/api.enhancer.ts`
**Endpoint:** `POST /api/enhancer`
**Handler:** `enhancerAction()`

**Input:**
```typescript
{
  message: string  // Original user prompt
}
```

**Output:** Streaming enhanced prompt text

**Features:**
- Improves user prompts using AI
- Returns only enhanced prompt (no explanation)
- Uses streaming response

#### 3. Page Routes

**Index Route:** `app/routes/_index.tsx`
- Main chat interface

**Chat History Route:** `app/routes/chat.$id.tsx`
- Load specific chat by ID

### Cloudflare Workers Function

**File:** `functions/[[path]].ts`

**Handler:** Catch-all page function

**Purpose:** Routes all requests through Remix on Cloudflare Pages

---

## 7. Prompt/Agent Infrastructure

### AI Prompt System

#### 1. System Prompt (`app/lib/.server/llm/prompts.ts`)

**Main Prompt:** `getSystemPrompt(cwd)`

**Structure:**
- **Role Definition:** "You are Bolt, an expert AI assistant..."
- **System Constraints:** WebContainer limitations
- **Code Formatting:** 2-space indentation
- **Message Formatting:** Allowed HTML elements
- **Diff Specification:** GNU unified diff format handling
- **Artifact Instructions:** Complete project generation rules

**Key Sections:**

**WebContainer Constraints:**
- Browser-based Node.js runtime
- Python stdlib only (no pip)
- No native binaries/compilers
- No Git
- Available shell commands listed

**Artifact Generation Rules:**
```xml
<boltArtifact id="..." title="...">
  <boltAction type="file" filePath="...">
    [file content]
  </boltAction>
  <boltAction type="shell">
    [shell command]
  </boltAction>
</boltArtifact>
```

**File Modification Handling:**
- Parses `<bolt_file_modifications>` tag
- Handles both `<diff>` and `<file>` formats
- GNU unified diff format parsing

**Continuation Prompt:**
```
Continue your prior response. IMPORTANT: Immediately begin from where you left off...
```

#### 2. Message Parser (`app/lib/runtime/message-parser.ts`)

**Purpose:** Extract structured data from AI responses

**Parsing Logic:**
- State machine-based streaming parser
- Handles partial/incomplete tags
- Extracts artifact metadata (id, title)
- Extracts action metadata (type, filePath)
- Separates content from tags

**Callbacks:**
- `onArtifactOpen` - New artifact detected
- `onArtifactClose` - Artifact complete
- `onActionOpen` - New action detected
- `onActionClose` - Action complete (ready to execute)

#### 3. LLM Configuration (`app/lib/.server/llm/`)

**Model:** Claude 3.5 Sonnet (claude-3-5-sonnet-20240620)

**Configuration:**
```typescript
maxTokens: 8192
headers: {
  'anthropic-beta': 'max-tokens-3-5-sonnet-2024-07-15'
}
toolChoice: 'none'
```

**Stream Handling:**
- Uses Vercel AI SDK's `streamText()`
- Converts to `AIStream` format
- Supports response continuation

#### 4. DotPrompt Workspace (`.prompt/`)

**Purpose:** Infrastructure for AI-assisted codebase analysis

**Files:**
- `.prompt/README.md` - Workspace documentation
- `.prompt/prompt-file-template.md` - 14-section IR template

**IR Template Sections:**
1. Purpose
2. Domain Role
3. Public API (Full Detail)
4. Internal Structure
5. Internal Behavior & Data Flow
6. Relationships & Collaboration
7. Database Interaction Mapping
8. UI Behavior
9. Key Logic Snippets
10. Architectural Concerns
11. Migration Mapping (Legacy → Modern)
12. Migration Concerns & Recommendations
13. Dependencies
14. Tags

**Use Case:** Document legacy codebases for modernization/migration

---

## 8. Recommended DotPrompt Plan Structure

Based on the repository analysis, here is the recommended plan structure for the `.prompt/plan/` directory:

### Recommended Structure

```
.prompt/plan/
├── app/
│   ├── server/
│   │   ├── llm-integration.md          # LLM/AI integration architecture
│   │   ├── api-routes.md               # API endpoint design
│   │   ├── ssr-rendering.md            # Server-side rendering strategy
│   │   └── streaming-architecture.md   # Streaming response handling
│   └── client/
│       ├── chat-ui.md                  # Chat interface architecture
│       ├── workbench-ide.md            # IDE/workbench components
│       ├── code-editor.md              # CodeMirror integration
│       ├── terminal-integration.md     # XTerm.js terminal
│       ├── file-explorer.md            # File tree component
│       ├── live-preview.md             # Preview iframe system
│       ├── state-management.md         # Nanostores architecture
│       └── ui-components.md            # Reusable UI components
├── shared/
│   ├── runtime/
│   │   ├── message-parser.md           # AI message parsing logic
│   │   ├── action-runner.md            # Action execution engine
│   │   └── artifact-lifecycle.md       # Artifact state management
│   ├── stores/
│   │   ├── workbench-store.md          # Main workbench orchestration
│   │   ├── files-store.md              # File system state
│   │   ├── editor-store.md             # Editor document state
│   │   ├── terminal-store.md           # Terminal state
│   │   └── chat-store.md               # Chat state
│   ├── webcontainer/
│   │   ├── integration.md              # WebContainer API integration
│   │   ├── filesystem-sync.md          # FS sync strategy
│   │   └── process-management.md       # Shell/process handling
│   ├── persistence/
│   │   ├── indexeddb.md                # IndexedDB schema & operations
│   │   └── chat-history.md             # Chat history persistence
│   └── types/
│       ├── domain-models.md            # Core domain types
│       ├── actions.md                  # Action type definitions
│       └── artifacts.md                # Artifact type definitions
├── db/
│   └── client-storage.md               # IndexedDB schema (no backend DB)
└── deployment/
    ├── cloudflare-pages.md             # Cloudflare Pages config
    ├── cloudflare-workers.md           # Edge function deployment
    └── environment-config.md           # Environment variables
```

### Rationale

**App/Server:**
- Focus on LLM integration, API routes, and streaming architecture
- Document SSR strategy with Remix
- Capture prompt engineering and continuation logic

**App/Client:**
- Separate concerns by major UI feature (chat, workbench, editor, terminal)
- Document state management patterns
- Capture component architecture and interactions

**Shared:**
- Core runtime logic (message parsing, action execution)
- State stores (central to the architecture)
- WebContainer integration (unique infrastructure)
- Persistence layer (IndexedDB)
- Type definitions (domain models)

**DB:**
- Document client-side storage (IndexedDB schema)
- No traditional backend database

**Deployment:**
- Cloudflare-specific deployment configuration
- Environment variable management

### Key Architectural Decisions to Document

1. **Streaming Architecture**: How AI responses stream and update UI in real-time
2. **Action Execution Model**: Sequential vs parallel, abort handling
3. **File System Sync**: WebContainer FS ↔ App State synchronization
4. **State Management**: Nanostores reactive architecture
5. **Client-Side Persistence**: IndexedDB usage patterns
6. **No Backend DB**: Fully client-side data storage
7. **Message Parsing**: Streaming XML-like tag parsing
8. **Artifact Lifecycle**: Open → Actions → Execute → Complete
9. **WebContainer Constraints**: What works, what doesn't (no pip, no git, etc.)
10. **Code Editor Integration**: CodeMirror document management

### Migration Considerations

If migrating to a different architecture:

**Consider:**
- Extracting LLM integration to separate service
- Adding backend database for chat history (Postgres, MongoDB, etc.)
- Replacing WebContainer with Docker/sandboxed environments
- Server-side action execution for security
- Separating frontend from backend into microservices

**Preserve:**
- Message parsing logic (reusable)
- Action type system (file/shell abstraction)
- Artifact concept (project generation unit)
- UI component architecture
- State management patterns

---

## Summary

**bolt.new** is a sophisticated full-stack TypeScript application that combines:
- Modern web framework (Remix)
- AI language model integration (Claude 3.5 Sonnet)
- In-browser development environment (WebContainer)
- Real-time streaming architecture
- Advanced code editor (CodeMirror 6)
- Comprehensive state management (Nanostores)

The codebase is well-organized with clear separation between:
- **Frontend**: UI components (chat, workbench, editor, terminal)
- **Backend**: LLM integration, API routes, SSR
- **Shared**: Runtime logic, state stores, types, utilities

**Key Technical Achievements:**
- Complete Node.js environment in the browser
- AI-driven code generation with structured output
- Real-time collaboration between AI and user
- No backend database (fully client-side)
- Edge deployment on Cloudflare

**Technology Stack:**
- Remix + React + TypeScript
- Nanostores + Vite + pnpm
- Anthropic Claude API + Vercel AI SDK
- WebContainer + CodeMirror + XTerm.js
- Cloudflare Pages + Workers

This represents a cutting-edge implementation of browser-based AI-assisted development tools.
