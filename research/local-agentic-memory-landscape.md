# Local Agentic Memory Systems — Research Report

**Date**: 2026-05-02  
**Scope**: Open-source agentic memory implementations that can run locally with local models  
**Search method**: SearXNG on localhost:8080 + web_search + GitHub API + cloned repos

---

## Executive Summary

The landscape has **three distinct architectural approaches**, each with different tradeoffs for local deployment:

| Approach | Projects | Local Model Support | Storage | Complexity |
|----------|----------|---------------------|---------|------------|
| **Markdown-native** | Ori-Mnemos, zer0dex | ✅ Full (BM25, no embeddings needed) | Markdown + SQLite | Low |
| **In-process vector** | cognis, ctxvault, mcp-memory-service | ⚠️ Partial (ONNX/fastembed) | SQLite + file-backed | Medium |
| **Server-based** | MemMachine, mnemory, Memary | ❌ Needs external services | PostgreSQL + Qdrant/Neo4j | High |

**Best match for our project**: Ori-Mnemos and zer0dex — both are markdown-native, local-first, and work without cloud dependencies.

---

## Project Deep Dives

### 1. Ori-Mnemos ⭐⭐⭐⭐⭐ (Best Match)

**Repo**: [aayoawoyemi/Ori-Mnemos](https://github.com/aayoawoyemi/Ori-Mnemos)  
**Stars**: 284 | **License**: Apache-2.0 | **Language**: TypeScript  
**Package**: `npm install -g ori-memory`

#### Architecture
- **Markdown on disk** — notes stored as plain `.md` files with YAML frontmatter
- **Wiki-links as graph edges** — `[[note-title]]` creates edges in the knowledge graph
- **BM25 keyword search** — pure text-based, no embeddings needed
- **BM25 + embedding + PageRank fusion** — optional embedding layer via OpenAI-compatible API
- **ACT-R activation decay** — memories fade based on retrieval frequency
- **Spreading activation** — retrieval follows wiki-link edges with dampening
- **Q-value reinforcement learning** — learns which retrieval paths are most useful
- **SQLite index** — lightweight metadata index (not the source of truth)

#### Local Model Support
- **BM25 search works fully offline** — no LLM or embeddings needed for retrieval
- **LLM provider is optional** — used only for note enhancement during promotion
- **OpenAI-compatible** — any local model server (llama.cpp, Ollama) works via `base_url` config
- **Embeddings optional** — BM25 + PageRank fusion works without embeddings

#### Memory Types
- Inbox → Promote → Permanent (staged promotion, like our memory-inbox → consolidator)
- Types: idea, decision, learning, insight, blocker, opportunity
- Project tags for scoping
- Warmth/activation scores for relevance ranking

#### Retrieval Pipeline
```
Query → BM25 keyword search → Graph signal (PageRank) → Warmth signal → RRF fusion → Ranked results
```

#### Benchmarks
- **HotpotQA**: 90% Recall@5 vs Mem0's 29% (3.1× better)
- **LoCoMo**: 37.69 single-hop, 29.31 multi-hop (vs Mem0's 38.72/28.64)
- **Latency**: 120ms avg vs Mem0's 1,140ms (9.5× faster)
- **Infrastructure**: Markdown + SQLite vs Redis + Qdrant + cloud

#### Key Source Files
- [`src/core/bm25.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/bm25.ts) — BM25 indexer
- [`src/core/fusion.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/fusion.ts) — RRF fusion engine
- [`src/core/graph.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/graph.ts) — wiki-link graph
- [`src/core/activation.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/activation.ts) — ACT-R decay
- [`src/core/ppr.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/ppr.ts) — Personalized PageRank
- [`src/providers/openai-compat.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/providers/openai-compat.ts) — LLM provider (optional)

#### Relevance to Our Project
- ✅ Markdown-native (matches our design principle)
- ✅ Staged inbox → promote workflow (matches our memory-inbox → consolidator contract)
- ✅ Works fully offline with BM25
- ✅ Optional LLM for enhancement only
- ✅ SQLite metadata index (rebuildable from Markdown)
- ✅ Knowledge graph via wiki-links
- ✅ Local-first, zero cloud dependency

---

### 2. zer0dex ⭐⭐⭐⭐

**Repo**: [hermes-labs-ai/zer0dex](https://github.com/hermes-labs-ai/zer0dex)  
**Stars**: 48 | **License**: Apache-2.0 | **Language**: Python  
**Package**: `pip install zer0dex`

#### Architecture
- **Dual-layer**: Compressed MEMORY.md index (~3KB, ~782 tokens) + vector store
- **Layer 1**: Human-readable semantic table of contents, always in context
- **Layer 2**: mem0ai + chromadb for semantic fact retrieval
- **Pre-message hook**: HTTP server queries vector store on every inbound message
- **Automatic injection**: Top 5 relevant memories injected into agent context

#### Local Model Support
- ⚠️ Uses **mem0ai** library which supports local embeddings via fastembed
- ⚠️ Uses **chromadb** (local file-backed mode available)
- ❌ Extraction still needs an LLM (OpenAI-compatible, so llama.cpp works)

#### Benchmarks
- 91.2% recall, 87% ≥75% pass rate, 80% cross-reference
- 70ms latency, fully local

#### Relevance to Our Project
- ✅ Compressed index idea is excellent (navigation scaffolding)
- ✅ Dual-layer pattern: human-readable index + semantic store
- ✅ Automatic pre-message injection
- ⚠️ Depends on mem0ai (adds cloud dependency risk)
- ⚠️ Vector store is not rebuildable from Markdown

---

### 3. mcp-memory-service ⭐⭐⭐⭐

**Repo**: [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service)  
**Stars**: 1,763 | **License**: Apache-2.0 | **Language**: Python  
**Package**: `pip install mcp-memory-service`

#### Architecture
- **REST API + MCP transport** — dual interface, framework-agnostic
- **Knowledge graph** — typed edges (causes, fixes, contradicts)
- **Autonomous consolidation** — compresses old memories automatically
- **ONNX embeddings** — embeddings run locally, no cloud needed
- **SQLite + sqlite-vec** — file-backed vector store
- **SSE events** — real-time notifications when memories change
- **OAuth 2.0 + DCR** — enterprise-ready auth

#### Local Model Support
- ✅ **ONNX embeddings** — fully local, no API keys needed
- ✅ **sqlite-vec** — file-backed vector store, zero external services
- ⚠️ Extraction/consolidation needs an LLM (OpenAI-compatible)

#### Features
- 15 REST endpoints
- Works with LangGraph, CrewAI, AutoGen, Claude Desktop, OpenCode
- Remote MCP support for claude.ai browser integration
- Web dashboard with semantic search, tag browser, analytics

#### Relevance to Our Project
- ✅ ONNX embeddings = fully local
- ✅ Knowledge graph with typed edges
- ✅ Autonomous consolidation
- ⚠️ Vector store is not Markdown-native
- ⚠️ More complex than needed for our use case
- ⚠️ SQLite-vec is not rebuildable from Markdown

---

### 4. ctxvault ⭐⭐⭐

**Repo**: [Filippo-Venturini/ctxvault](https://github.com/Filippo-Venturini/ctxvault)  
**Stars**: 52 | **License**: MIT | **Language**: Python  
**Package**: `pip install ctxvault`

#### Architecture
- **Typed memory vaults** — semantic vault (knowledge) + skill vault (procedures)
- **Structural isolation** — each vault is independent, with access control
- **ChromaDB** — local file-backed vector store
- **Directory-backed** — vaults are plain directories on disk
- **MCP server + HTTP API + CLI** — triple interface

#### Local Model Support
- ⚠️ Uses OpenAI embeddings by default
- ⚠️ Supports OpenAI-compatible APIs (llama.cpp works)
- ⚠️ No built-in local embedding option

#### Relevance to Our Project
- ✅ Typed memory (semantic vs procedural) is a great idea
- ✅ Structural isolation and access control
- ✅ Directory-backed, observable
- ❌ Requires external embedding service
- ❌ Vector store, not Markdown-native

---

### 5. mnemory ⭐⭐⭐

**Repo**: [fpytloun/mnemory](https://github.com/fpytloun/mnemory)  
**Stars**: 99 | **License**: Apache-2.0 | **Language**: Python  
**Package**: `uvx mnemory`

#### Architecture
- **Two-tier memory** — fast searchable summaries (vector) + detailed artifacts (S3/MinIO)
- **Intelligent extraction** — single LLM call for facts, metadata, dedup
- **Contradiction resolution** — "I drive a Skoda" → "I bought a Tesla" = auto-update
- **Memory health checks** — fsck detects duplicates, contradictions, injection
- **10+ client support** — Claude Code, ChatGPT, Cursor, Windsurf, etc.
- **Built-in management UI** — dashboard, search, graph visualization

#### Local Model Support
- ✅ **fastembed** — local embeddings via sentence-transformers
- ⚠️ Extraction needs LLM (OpenAI-compatible)
- ⚠️ Qdrant vector store (can run locally via Docker)
- ⚠️ S3/MinIO for artifacts (optional but adds complexity)

#### Relevance to Our Project
- ✅ fastembed = local embeddings
- ✅ Contradiction resolution is valuable
- ✅ Health checks (fsck) are useful
- ❌ Qdrant adds infrastructure dependency
- ❌ Not Markdown-native
- ❌ More complex than our needs

---

### 6. cognis ⭐⭐⭐

**Repo**: [Lyzr-Cognis/cognis](https://github.com/Lyzr-Cognis/cognis)  
**Stars**: 50 | **License**: MIT | **Language**: Python  
**Package**: `pip install lyzr-cognis`

#### Architecture
- **In-process** — runs inside your Python app, no server
- **Hybrid search** — Matryoshka vector search (256D shortlist, 768D rerank) + BM25 via SQLite FTS5
- **RRF fusion** — 70/30 split, tuned from ablation studies
- **13 auto-tagged categories** — smart extraction with memory versioning
- **Qdrant local mode** — file-backed, no server needed
- **~500ms search latency**

#### Local Model Support
- ❌ Uses **Gemini API for embeddings** (not local)
- ❌ Uses **OpenAI for extraction** (gpt-4.1-mini)
- ⚠️ Qdrant local mode is file-backed
- ⚠️ BM25 via SQLite FTS5 works offline

#### Relevance to Our Project
- ✅ In-process, zero infrastructure
- ✅ Hybrid search with BM25 fallback
- ✅ Smart extraction with versioning
- ❌ Requires Gemini + OpenAI API keys
- ❌ Not Markdown-native

---

### 7. MemMachine ⭐⭐

**Repo**: [MemMachine/MemMachine](https://github.com/MemMachine/MemMachine)  
**Stars**: 3,546 | **License**: Apache-2.0 | **Language**: Python  
**Package**: `pip install memmachine-client`

#### Architecture
- **Server-based** — requires running MemMachine server
- **Episodic memory** — graph-based conversational context
- **Profile memory** — user facts in SQL
- **Working memory** — short-term session context
- **Agent memory persistence** — survives restarts and model changes
- **Sentence-transformer embeddings** — local embedding option

#### Local Model Support
- ✅ Supports **sentence-transformer** embeddings (local)
- ✅ Supports **OpenAI-compatible** LLMs
- ❌ Requires PostgreSQL + Neo4j/FalkorDB
- ❌ Docker compose needed for full stack

#### Relevance to Our Project
- ✅ Most mature, most stars
- ✅ Comprehensive memory types
- ❌ Heavy infrastructure (PostgreSQL, Neo4j, Docker)
- ❌ Not Markdown-native
- ❌ Server-based, not local-first

---

### 8. Memary ⭐⭐

**Repo**: [kingjulio8238/Memary](https://github.com/kingjulio8238/Memary)  
**Stars**: 2,603 | **License**: MIT | **Language**: Python  
**Package**: `pip install memary`

#### Architecture
- **Human memory emulation** — episodic, semantic, procedural memory layers
- **Graph database** — FalkorDB or Neo4j required
- **Vision model** — for visual memory (LLaVA or GPT-4-vision)
- **Streamlit UI** — web dashboard
- **Multi-agent support** — separate graphs per agent

#### Local Model Support
- ✅ Supports **Ollama** for LLM (Llama 3 8B/40B)
- ✅ Supports **Ollama** for vision (LLaVA)
- ❌ Requires **FalkorDB or Neo4j** (graph database)
- ❌ Requires OpenAI, Perplexity, Google Maps, Alpha Vantage APIs

#### Relevance to Our Project
- ✅ Human memory model is interesting
- ✅ Ollama support for local models
- ❌ Heavy infrastructure (graph DB + multiple APIs)
- ❌ Not Markdown-native
- ❌ Requires many API keys

---

### 9. Signet-AI ⭐⭐

**Repo**: [Signet-AI/signetai](https://github.com/Signet-AI/signetai)  
**Stars**: 134 | **License**: Apache-2.0 | **Language**: TypeScript  
**Package**: `npm install -g signetai`

#### Architecture
- **Portable context layer** — works across agents, models, harnesses
- **Ambient memory** — captures context between sessions automatically
- **Raw record preservation** — keeps original text, indexes for recall
- **97.6% LongMemEval** — high recall accuracy
- **Bun/Node runtime** — TypeScript-based

#### Local Model Support
- ⚠️ Uses OpenAI-compatible APIs
- ⚠️ Docker self-hosting available
- ⚠️ Not designed for fully offline use

#### Relevance to Our Project
- ✅ Portable context across agents
- ✅ Raw record preservation
- ✅ High recall accuracy
- ❌ Not fully local-first
- ❌ Not Markdown-native

---

### 10. memsearch ⭐⭐⭐

**Repo**: [zilliztech/memsearch](https://github.com/zilliztech/memsearch)  
**License**: Apache-2.0 | **Language**: Python  
**Package**: `pip install memsearch`

#### Architecture
- **Markdown source of truth** — inspired by OpenClaw, memories are `.md` files
- **Milvus shadow index** — derived, rebuildable vector cache
- **3-layer recall** — search → expand → transcript
- **Hybrid search** — dense vector + BM25 sparse + RRF reranking
- **SHA-256 content hashing** — skips unchanged content during reindex
- **File watcher** — auto-indexes in real time
- **Cross-platform** — Claude Code, OpenClaw, OpenCode, Codex CLI

#### Local Model Support
- ⚠️ Milvus vector store (can run locally via Docker)
- ⚠️ Embeddings need provider (OpenAI-compatible)

#### Relevance to Our Project
- ✅ Markdown source of truth
- ✅ Rebuildable shadow index
- ✅ Hybrid search (BM25 + vector + RRF)
- ✅ Cross-platform memory sharing
- ❌ Milvus adds infrastructure dependency
- ❌ Not fully offline

---

### 11. memtomem ⭐⭐⭐⭐

**Repo**: [memtomem/memtomem](https://github.com/memtomem/memtomem)  
**License**: Apache-2.0 | **Language**: Python  
**Package**: `pip install memtomem`

#### Architecture
- **Markdown-first** — `.md` files are source of truth, DB is rebuildable cache
- **Hybrid search** — BM25 keyword + ONNX semantic similarity
- **ONNX embeddings** — `bge-small-en-v1.5` runs locally
- **Minimal mode** — BM25-only install (~40MB vs ~250MB with embeddings)
- **MCP server** — tools for index, search, add, status
- **Auto-discover providers** — Ollama, OpenAI

#### Local Model Support
- ✅ **ONNX embeddings** — fully local, no API keys
- ✅ **BM25-only mode** — works fully offline
- ✅ **Ollama provider** — local LLM for extraction

#### Relevance to Our Project
- ✅ Markdown source of truth
- ✅ Rebuildable cache
- ✅ BM25-only mode (fully offline)
- ✅ ONNX embeddings (local)
- ✅ Ollama provider support
- ⚠️ Python-based (our inbox is Python, consolidator could be too)

---

### 12. local-memory-platform ⭐⭐⭐⭐

**Repo**: [monxas/local-memory-platform](https://github.com/monxas/local-memory-platform)  
**License**: MIT | **Language**: Python

#### Architecture
- **Markdown-first** — `MEMORY.md` + `memory/*.md`
- **Hybrid search** — TF-IDF semantic + BM25 exact matching
- **Explainable ranking** — `score`, `tfidf_score`, `bm25_score`, `score_parts`, `why`
- **SQLite metadata** — indexed files, rebuild history, search telemetry
- **Soft-forget** — deprecation instead of destructive deletion
- **Golden query regression tests** — catch retrieval regressions
- **Daily distillation helper** — compress daily notes
- **Health gate for CI/cron** — automated quality checks

#### Local Model Support
- ✅ **No hosted embeddings required** — pure TF-IDF + BM25
- ✅ **Fully offline** — zero cloud dependencies

#### Relevance to Our Project
- ✅ Markdown source of truth
- ✅ Explainable ranking (score breakdown)
- ✅ Soft-forget lifecycle (matches our retention design)
- ✅ Golden query regression tests (excellent for quality)
- ✅ Fully offline, no embeddings needed
- ✅ SQLite metadata (rebuildable)

---

### 13. remnic ⭐⭐⭐⭐

**Repo**: [joshuaswarren/remnic](https://github.com/joshuaswarren/remnic)  
**License**: MIT | **Language**: TypeScript  
**Package**: `npm install -g @remnic/cli`

#### Architecture
- **Markdown files** — every memory is a `.md` with YAML frontmatter
- **QMD hybrid search** — BM25 + vector + reranking (OpenClaw's search engine)
- **3 retrieval tiers** — chunk → section → raw transcript
- **PageRank graph retrieval** — feature-flagged, follows entity links
- **Memory-worth scoring** — filters low-value facts before LLM
- **Temporal supersession** — keeps stale facts out of recall
- **Background consolidation** — "dreams" merge duplicates, promote themes
- **Provenance tracking** — `derived_from`, `derived_via` fields
- **Procedural memory** — captures multi-step runbooks

#### Local Model Support
- ✅ **Local LLM support** — Ollama, LM Studio for extraction
- ⚠️ QMD vector search needs embeddings (configurable provider)
- ✅ **BM25 fallback** — works without embeddings

#### Relevance to Our Project
- ✅ Markdown source of truth
- ✅ Background consolidation (matches our consolidator concept)
- ✅ Provenance tracking (matches our candidate metadata)
- ✅ Temporal supersession (matches our retention design)
- ✅ Procedural memory (matches our memory types)
- ✅ Memory-worth scoring (matches our triage flags)
- ⚠️ QMD adds complexity

---

### 14. agentmemory ⭐⭐⭐⭐⭐

**Repo**: [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)  
**License**: MIT | **Language**: TypeScript  
**Package**: `npm install -g @agentmemory/agentmemory`

#### Architecture
- **Karpathy-style LLM wiki** — Markdown + Git as memory layer
- **Confidence scoring** — tracks how reliable each memory is
- **Lifecycle management** — create, update, archive, delete
- **Knowledge graphs** — entity relationships
- **Hybrid search** — BM25 + semantic
- **0 external DBs** — everything local
- **51 MCP tools** — comprehensive toolset
- **12 auto hooks** — automatic capture on events
- **95.2% retrieval R@5** — high recall
- **92% fewer tokens** — efficient context injection

#### Local Model Support
- ✅ **0 external DBs** — fully local
- ✅ **Ollama support** — local LLM for extraction
- ⚠️ Semantic search needs embeddings (configurable)

#### Relevance to Our Project
- ✅ Karpathy-style wiki pattern (Markdown + Git)
- ✅ Confidence scoring (matches our triage flags)
- ✅ Lifecycle management (matches our retention design)
- ✅ 0 external DBs
- ✅ High recall with few tokens
- ✅ Auto hooks (matches our Pi extension hooks)

---

### 15. cognee ⭐⭐⭐

**Repo**: [topoteretes/cognee](https://github.com/topoteretes/cognee) (16,982⭐)  
**License**: Apache-2.0 | **Language**: Python  
**Package**: `pip install cognee`

#### Architecture
- **Knowledge engine** — ingest data in any format, continuously learns
- **Graph + vector hybrid** — Neo4j, PostgreSQL, Kùzu, Neptune for graph; Chroma, Qdrant for vectors
- **ECL pipeline** — Extract, Cognify, Load (entities → relationships → storage)
- **Session memory** — fast cache, syncs to permanent graph in background
- **Ontology grounding** — custom schemas for domain-specific knowledge
- **Multimodal** — text, images, documents
- **Agentic feedback** — learns from user feedback
- **Cross-agent sharing** — unified knowledge across agents
- **Plugins** — Claude Code, OpenClaw, Hermes Agent

#### Local Model Support
- ✅ **Ollama provider** — local LLM for extraction/cognification
- ✅ **fastembed** — local ONNX embeddings (`pip install cognee[fastembed]`)
- ✅ **PostgreSQL graph** — runs locally via Docker
- ⚠️ **Heavy infrastructure** — Neo4j, Chroma, Postgres all need setup
- ❌ Not truly "zero infra" — requires multiple services

#### Relevance to Our Project
- ✅ Knowledge graph + vector hybrid
- ✅ Session memory pattern (fast cache → permanent)
- ✅ Feedback learning loop
- ❌ Heavy infrastructure (Neo4j, Chroma, Postgres)
- ❌ Not Markdown-native
- ❌ Complex setup for local deployment

---

### 16. MemPalace ⭐⭐⭐⭐⭐

**Repo**: [mempalace/mempalace](https://github.com/mempalace/mempalace) (50,774⭐)  
**License**: MIT | **Language**: Python  
**Package**: `pip install mempalace`

#### Architecture
- **Verbatim storage** — stores conversation history as-is, no summarization
- **Palace structure** — people/projects = *wings*, topics = *rooms*, content = *drawers*
- **Pluggable backend** — default ChromaDB, interface in `backends/base.py`
- **Semantic search** — ONNX `all-MiniLM-L6-v2` (384-dim, CPU/GPU/CoreML/DirectML)
- **Hybrid retrieval** — keyword boosting + temporal proximity + preference patterns
- **Conversation mining** — `mempalace mine` for project files or Claude sessions
- **Wake-up command** — `mempalace wake-up` loads context for new sessions
- **Deduplication** — built-in content dedup
- **Entity detection** — people, projects, topics auto-extracted

#### Local Model Support
- ✅ **ONNX embeddings** — fully local, hardware-accelerated (CPU/CUDA/CoreML/DirectML)
- ✅ **No API calls required** — raw 96.6% recall with zero external services
- ✅ **Ollama rerank** — optional LLM rerank via Ollama for ≥99% recall
- ⚠️ **ChromaDB default** — can run locally but adds dependency

#### Benchmarks
- **LongMemEval R@5**: 96.6% raw (no LLM), 98.4% hybrid, ≥99% with rerank
- **LoCoMo R@10**: 60.3% raw, 88.9% hybrid
- **ConvoMem**: 92.9% avg recall (250 items)
- **MemBench**: 80.3% R@5 (8,500 items)

#### Relevance to Our Project
- ✅ Verbatim storage (matches our candidate capture)
- ✅ ONNX embeddings (fully local)
- ✅ Hardware acceleration (CPU/CUDA/CoreML/DirectML)
- ✅ Conversation mining (matches our Pi extension hooks)
- ✅ Pluggable backend (could swap Chroma for SQLite)
- ✅ Palace structure (wing/room/drawer = hierarchical memory)
- ⚠️ ChromaDB adds infrastructure
- ❌ No Markdown source of truth (Chroma is the source)

---

## Comparison Matrix (Updated)

| Feature | Ori-Mnemos | zer0dex | mcp-memory | mnemory | cognis | ctxvault | MemMachine | Memary | Signet |
|---------|-----------|---------|-----------|---------|--------|----------|------------|--------|--------|
| **Markdown-native** | ✅ | ✅ (index) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Fully offline** | ✅ (BM25) | ⚠️ | ✅ | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Local embeddings** | Optional | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Knowledge graph** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Inbox → promote** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Rebuildable indexes** | ✅ | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **MCP support** | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Consolidation** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Stars** | 284 | 48 | 1,763 | 99 | 50 | 52 | 3,546 | 2,603 | 134 |

---

## Key Insights

### 1. Markdown-native is now the dominant pattern for local memory
**7 of 14 projects** use Markdown as source of truth: Ori-Mnemos, zer0dex, memsearch, memtomem, local-memory-platform, remnic, agentmemory. This validates our design principle. The pattern is: Markdown files on disk + rebuildable index/cache.

### 2. BM25 + graph beats pure vector search
Ori-Mnemos benchmarks show BM25 + PageRank fusion outperforms Mem0's vector-based approach (3.1× better recall, 9.5× faster) with zero cloud dependencies. **memtomem** and **local-memory-platform** also prove BM25-only mode works well.

### 3. Inbox → promote pattern is unique to Ori-Mnemos
Our memory-inbox → consolidator contract maps directly to Ori-Mnemos' inbox → promote workflow. No other project implements staged memory promotion. **remnic** has background consolidation but not staged inbox.

### 4. Local embeddings are becoming standard
fastembed (mnemory), ONNX (mcp-memory-service, memtomem), and sentence-transformers (MemMachine) all provide local embedding options. **memtomem** offers BM25-only minimal install (~40MB) as fallback.

### 5. Knowledge graphs add value but cost complexity
Typed edges (mcp-memory-service) and wiki-links (Ori-Mnemos) both work, but graph databases (Memary, MemMachine) add heavy infrastructure. Ori-Mnemos' wiki-link approach is the lightest. **remnic** adds PageRank graph retrieval as optional feature.

### 6. Explainable ranking is undervalued
**local-memory-platform** provides `score_parts` and `why` fields showing exactly why each result ranked highly. This is critical for debugging retrieval quality. **remnic** has Recall X-ray for similar transparency.

### 7. Lifecycle management matters
**remnic** (temporal supersession, soft-forget), **local-memory-platform** (soft-forget/deprecation), and **agentmemory** (confidence scoring, lifecycle) all implement memory lifecycle. Our consolidator needs this too.

### 8. Golden query regression tests are essential
**local-memory-platform** implements golden queries to catch retrieval regressions. This is critical for maintaining quality as the memory corpus grows.

### 9. Verbatim vs extracted memory is a real design choice
**MemPalace** stores conversations verbatim (no summarization) and achieves 96.6% raw recall with ONNX embeddings alone. This challenges the assumption that extraction/summarization is required. For our consolidator, we might consider a hybrid: capture verbatim in inbox, extract/summarize during consolidation.

### 10. Knowledge graphs add power but cost complexity
**Cognee** (16,982⭐) shows graph + vector hybrid works well but requires Neo4j/PostgreSQL + Chroma/Qdrant. **MemPalace** (50,774⭐) shows verbatim storage + semantic search can achieve 96.6% recall with minimal infrastructure. For our local-first design, MemPalace's approach is more aligned.

### 11. Hardware acceleration matters for local embeddings
**MemPalace** supports CPU, CUDA, CoreML, and DirectML for ONNX embeddings. This means local embeddings can be fast on any hardware. Our consolidator should support hardware-accelerated ONNX embeddings for optimal performance.

---

## Recommendations for Our Memory Consolidator

### Core Architecture (Ori-Mnemos + memtomem + local-memory-platform)

1. **Markdown on disk** — keep our existing candidate Markdown format
2. **BM25 search** — implement keyword search that works fully offline
3. **Wiki-links as graph edges** — candidates can link to existing notes via `[[title]]`
4. **RRF fusion** — combine BM25 + graph signal + activation scores
5. **ACT-R activation decay** — memories fade based on usage
6. **SQLite metadata index** — rebuildable from Markdown frontmatter
7. **Optional LLM** — use local model for enhancement/consolidation when available
8. **Explainable ranking** — `score_parts` and `why` fields for debugging
9. **Golden query regression tests** — catch retrieval regressions

### What to skip initially

- **Vector embeddings** — not needed initially; BM25 works great for our use case
- **Graph database** — wiki-links in Markdown are sufficient
- **Server mode** — in-process library is simpler
- **MCP transport** — Pi extension is our integration surface

### What to add from other projects

- **Contradiction resolution** (from mnemory) — detect and resolve conflicting memories
- **Compressed index** (from zer0dex) — small navigational summary always in context
- **Health checks** (from mnemory) — fsck for detecting duplicates, stale notes
- **Typed memory** (from ctxvault) — semantic vs procedural memory separation
- **Soft-forget lifecycle** (from local-memory-platform) — deprecation instead of deletion
- **Confidence scoring** (from agentmemory) — track how reliable each memory is
- **Background consolidation** (from remnic) — merge duplicates, promote themes
- **Provenance tracking** (from remnic) — `derived_from`, `derived_via` fields
- **Memory-worth scoring** (from remnic) — filter low-value facts before LLM
- **Temporal supersession** (from remnic) — keep stale facts out of recall
- **SHA-256 content hashing** (from memsearch) — skip unchanged content during reindex
- **File watcher** (from memsearch) — auto-index in real time

### Reference Implementations to Study

| Feature | Best Reference |
|---------|---------------|
| BM25 search | Ori-Mnemos `src/core/bm25.ts` |
| RRF fusion | Ori-Mnemos `src/core/fusion.ts` |
| Wiki-link graph | Ori-Mnemos `src/core/graph.ts` |
| Activation decay | Ori-Mnemos `src/core/activation.ts` |
| PageRank | Ori-Mnemos `src/core/ppr.ts` |
| Explainable ranking | local-memory-platform (score_parts, why) |
| Soft-forget | local-memory-platform (deprecation workflow) |
| Golden queries | local-memory-platform (regression tests) |
| Hybrid search | memtomem (BM25 + ONNX) |
| Background consolidation | remnic ("dreams" surface) |
| Confidence scoring | agentmemory (lifecycle + confidence) |
| Contradiction resolution | mnemory (auto-update on conflicts) |
| Compressed index | zer0dex (MEMORY.md ~3KB) |
| Content hashing | memsearch (SHA-256 dedup) |
| Verbatim storage | mempalace (no summarization) |
| Hardware acceleration | mempalace (ONNX CPU/CUDA/CoreML/DirectML) |
| Palace structure | mempalace (wing/room/drawer hierarchy) |
| Graph + vector hybrid | cognee (ECL pipeline, Neo4j/Postgres) |
| Session memory | cognee (fast cache → permanent graph) |

---

## Source Code References

All Ori-Mnemos links point to the main branch. For permanent links, use commit SHAs from the repo.

Key Ori-Mnemos modules worth studying:
- **BM25**: [`src/core/bm25.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/bm25.ts)
- **Fusion**: [`src/core/fusion.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/fusion.ts)
- **Graph**: [`src/core/graph.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/graph.ts)
- **Activation**: [`src/core/activation.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/activation.ts)
- **PageRank**: [`src/core/ppr.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/ppr.ts)
- **Config**: [`src/core/config.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/config.ts)
- **Vault**: [`src/core/vault.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/vault.ts)
- **Promote**: [`src/core/promote.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/core/promote.ts)
- **CLI init**: [`src/cli/init.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/cli/init.ts)
- **MCP serve**: [`src/cli/serve.ts`](https://github.com/aayoawoyemi/Ori-Mnemos/blob/main/src/cli/serve.ts)
