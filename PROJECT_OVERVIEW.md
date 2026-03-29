# 📘 FindX — AI Based Knowledge Lookup

## Complete Project Overview

---

## 📌 Table of Contents

1. [What is FindX?](#what-is-findx)
2. [The Problem We Solve](#the-problem-we-solve)
3. [How FindX Works — The Big Picture](#how-findx-works--the-big-picture)
4. [Key Features](#key-features)
5. [Who is This For?](#who-is-this-for)
6. [Real-World Use Cases & Scenarios](#real-world-use-cases--scenarios)
7. [Product Walkthrough](#product-walkthrough)
8. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
9. [Project Scope & Limitations](#project-scope--limitations)
10. [Future Roadmap](#future-roadmap)
11. [About the Team](#about-the-team)

---

## What is FindX?

**FindX** is an **AI-powered knowledge lookup chatbot** that allows users to upload any structured data file (Excel spreadsheets, CSV files, or plain text documents) and then ask natural-language questions about that data — receiving accurate, instant, human-readable answers powered by artificial intelligence.

Think of it like having a **personal AI analyst** that reads your entire dataset and can answer any question you throw at it — in plain English.

### One-Line Summary

> **"Upload your data. Ask questions. Get instant, accurate answers — grounded in your actual data."**

### Why "FindX"?

The name **FindX** represents the core mission of the product — **finding the unknown (X) in your data**. Just like solving for "X" in mathematics, FindX solves the unknown in your knowledge base. Whether the answer is hidden in row 47 of a spreadsheet or scattered across thousands of text entries, FindX will find it for you.

---

## The Problem We Solve

### The Challenge: Data is Everywhere, Answers are Nowhere

In every organization — whether it's a logistics company, a college, a hospital, or a small business — data is stored in **Excel files, CSV exports, text logs, and spreadsheets**. When someone needs an answer, the traditional process looks like this:

1. 📂 **Open the file** — Find the right spreadsheet (which one was it again?)
2. 🔍 **Search manually** — Scroll through hundreds or thousands of rows
3. 🧮 **Apply filters** — Try Ctrl+F, column filters, or VLOOKUP
4. 🤔 **Interpret the data** — What does "Status: In Transit" mean for SHP001? Is there a delay?
5. ⏱️ **Time wasted** — This entire process takes 5-30 minutes per question

### The FindX Solution

With FindX, the same process takes **under 5 seconds**:

1. 📤 **Upload your file** — Drop your Excel/CSV file into FindX (one time)
2. 💬 **Ask a question** — Type: *"Which shipments are delayed?"*
3. ✅ **Get an instant answer** — FindX responds with a clear, formatted answer listing every delayed shipment with all relevant details

**No formulas. No filters. No technical expertise. Just answers.**

---

## How FindX Works — The Big Picture

FindX uses a technology called **RAG (Retrieval-Augmented Generation)** — a cutting-edge AI technique that combines the power of **search** and **language generation** to give accurate, grounded answers.

### Step-by-Step: What Happens When You Use FindX

#### Step 1: Upload Your Data 📤

You upload a file (e.g., `shipments.xlsx`) through the FindX dashboard. The system accepts:
- **Excel files** (.xlsx, .xls) — Spreadsheets with rows and columns
- **CSV files** (.csv) — Comma-separated data exports
- **Text files** (.txt) — Plain text documents or notes

#### Step 2: The AI Reads & Understands Your Data 🧠

Once uploaded, FindX doesn't just store your data — it **understands** it:

1. **Parsing**: Every row in your spreadsheet is converted into a descriptive text sentence. For example, a row like `SHP001 | In Transit | FedEx | New York → Los Angeles` becomes: *"shipment_id: SHP001. status: In Transit. carrier: FedEx. origin: New York. destination: Los Angeles."*

2. **Embedding**: Each text sentence is converted into a **384-dimensional mathematical vector** (a list of 384 numbers) using an AI model called `all-MiniLM-L6-v2`. These numbers capture the **meaning** of each sentence — not just the words. So "shipment via FedEx" and "FedEx delivery" would have similar vectors, even though the words are different.

3. **Indexing**: All vectors are stored in a **FAISS index** — an ultra-fast search engine built by Meta (Facebook) that can search millions of vectors in milliseconds.

#### Step 3: Ask a Question 💬

You type a question in the FindX chat: *"What is the status of shipment SHP001?"*

Your question goes through the same embedding process — it gets converted into a 384-dimensional vector that captures its meaning.

#### Step 4: Find the Most Relevant Data 🔍

FAISS compares your question's vector against all the data vectors and finds the **top 3 most similar** pieces of information in your dataset. This is called **semantic search** — it finds information based on **meaning**, not just keywords.

For example, if you ask "Which items are running late?", FindX will find records with statuses like "Delayed", "Pending", and "In Transit" — even though you didn't use those exact words.

#### Step 5: Generate the Answer 🤖

The 3 most relevant data excerpts (called **context**) are sent to an AI language model — **Llama 3.1 8B** (an open-source model by Meta) running on **Groq's** ultra-fast inference platform.

The AI model is instructed to:
- ✅ **Only answer from the provided context** — no making things up
- ✅ **Be clear and well-formatted** — use bullet points, numbers, and structure
- ✅ **Say "I don't know" if the data doesn't contain the answer** — honesty over hallucination

#### Step 6: See the Answer with Sources 📊

You receive:
- A **clear, formatted answer** in the chat
- **Source citations** — the exact data records the answer was based on, so you can verify it yourself

---

## Key Features

### 🧠 Semantic Search (Not Keyword Search)
Traditional search requires you to know the exact words in your data. FindX understands the **meaning** of your question. Ask "Which products are running behind schedule?" and it will find records with "Delayed" or "Pending" status — even though you never used those words.

### ⚡ Instant Answers (Under 2 Seconds)
Powered by Groq's ultra-fast AI inference platform, FindX generates responses in under 2 seconds — faster than opening an Excel file.

### 📁 Multi-Format Support
Upload any common data format:
- `.xlsx` / `.xls` — Microsoft Excel spreadsheets
- `.csv` — Comma-separated value files (exported from databases, Google Sheets, etc.)
- `.txt` — Plain text documents, notes, or logs

### 🎯 Grounded Answers (No Hallucinations)
Every answer comes with **source citations**. The AI strictly answers from your data — if the data doesn't contain the answer, it will honestly say so. No fabricated information, no guessing.

### 🔄 Live Re-Indexing
Upload a new file anytime to update your knowledge base. The system re-indexes on the fly — no restart needed.

### 💬 Chat History & Sessions
Your conversations are saved in the browser. Come back later and pick up where you left off.

### 📊 Management Dashboard
A full dashboard to:
- View how many documents are indexed
- See engine status (Active/Offline)
- Upload new files
- View recent query history
- Access API documentation

### 🔐 100% Open Source Stack
Every component used is either open-source or free-tier:
- **FastAPI** — Web framework
- **FAISS** — Vector search engine (by Meta)
- **SentenceTransformers** — Embedding model
- **Groq** — Free-tier AI inference
- **Llama 3.1** — Open-source language model (by Meta)

No expensive cloud services. No vendor lock-in. No monthly subscriptions.

---

## Who is This For?

### 👨‍💼 Business Users
*"I don't know SQL or Python. I just want to ask questions about my sales data."*

FindX is designed for non-technical users. If you can type a question, you can use FindX.

### 📦 Logistics & Supply Chain
*"I need to quickly check the status of shipments, find delays, and track carriers."*

Upload your shipment tracker spreadsheet and ask: "Which shipments are delayed in January 2024?"

### 🏫 Educational Institutions
*"We have student records in Excel. Teachers need to quickly look up specific information."*

Upload the student database and ask: "Who scored above 90 in mathematics?"

### 🏥 Healthcare Administration
*"Patient records are in spreadsheets. We need quick lookups without complex queries."*

Upload patient data and ask: "Which patients have appointments next Monday?"

### 📊 Any Organization with Spreadsheet Data
If your data lives in Excel, CSV, or text files, FindX can make it instantly searchable.

---

## Real-World Use Cases & Scenarios

### Scenario 1: Logistics Company — Shipment Tracking

**The Data**: `shipments.xlsx` containing 10,000 shipments with columns: Shipment ID, Status, Carrier, Origin, Destination, Delivery Date, Value, Weight, Remarks.

**User Questions & FindX Answers**:

| Question | FindX Response |
|---|---|
| "Which shipments are delayed?" | Lists all shipments with "Delayed" status, including carrier and expected delivery date |
| "What is the total value of FedEx shipments?" | Calculates and reports the sum |
| "Show me all shipments going to Los Angeles" | Lists every shipment with destination "Los Angeles" |
| "Which carrier has the most shipments?" | Identifies the carrier with the highest count |

### Scenario 2: College — Student Records

**The Data**: `students.csv` with 500 students — Name, Roll Number, Department, GPA, Attendance, Contact Info.

| Question | FindX Response |
|---|---|
| "Who has the highest GPA in Computer Science?" | Returns the student name, roll number, and GPA |
| "List students with less than 75% attendance" | Returns all students below the threshold |
| "How many students are in the IT department?" | Returns the count |

### Scenario 3: Retail — Inventory Management

**The Data**: `inventory.xlsx` — Product Name, SKU, Quantity, Warehouse Location, Reorder Level, Supplier.

| Question | FindX Response |
|---|---|
| "Which products are below reorder level?" | Lists products where quantity < reorder level |
| "What items are stored in Warehouse B?" | Lists all products in that location |
| "Who supplies the most products?" | Identifies the top supplier |

---

## Product Walkthrough

### Page 1: Landing Page (index.html)
The first page users see when they visit FindX. It features:
- A **hero section** with the tagline *"Unlock Insights from Any Knowledge Base"*
- A **login card** with glassmorphism design (email + password)
- **Feature cards** explaining the platform's capabilities (Semantic Search, Groq LLM Speed, Multi-Format Upload, Grounded Answers, Live Re-Indexing, Open Source Stack)
- A **"How It Works"** section showing the 4-step pipeline (Upload → Embed → Retrieve → Generate)
- A demo account button for instant access

### Page 2: Chat Interface (chat.html)
The core of FindX — a full-screen AI chatbot with:
- **Left sidebar**: Quick suggestions, file upload button, chat history, session management, configurable sources-per-query
- **Center area**: Chat messages with user bubbles (purple) and AI bubbles (dark), typing animation, source citations panel
- **Bottom input bar**: Text area with send button, file attachment, Enter-to-send shortcut
- **Status indicator**: Shows "Ready" (green) + document count when the engine is loaded

### Page 3: Dashboard (dashboard.html)
A management panel with:
- **Stats cards**: Documents indexed, queries this session, engine status, embedding model
- **Knowledge Base info**: Index loaded status, document count, embedding model, LLM model, index file path
- **Upload zone**: Drag-and-drop file upload with live progress and success/error feedback
- **Query history table**: Recent queries with answer previews and source counts
- **API quick reference**: All endpoint documentation inline

---

## Frequently Asked Questions (FAQ)

### Q: Do I need to know programming to use FindX?
**A**: No! FindX is designed for anyone. If you can type a question in English, you can use FindX. The technical setup only needs to be done once.

### Q: What kind of files can I upload?
**A**: Excel files (.xlsx, .xls), CSV files (.csv), and plain text files (.txt).

### Q: Is my data sent to the cloud?
**A**: Your data is processed locally on the machine running FindX. The only external call is to Groq's API to generate the final answer — but Groq only receives the relevant text snippets, not your entire file.

### Q: How accurate are the answers?
**A**: FindX only answers from the data you provide. It will never make up information. Every answer includes source citations so you can verify it yourself.

### Q: Can I change the uploaded data?
**A**: Yes! Simply upload a new file on the dashboard or through the chat sidebar. The system re-indexes immediately — no restart needed.

### Q: How many documents can FindX handle?
**A**: FindX uses FAISS, which can handle millions of vectors. For typical spreadsheets (up to 100,000 rows), performance is instant.

### Q: Is FindX free to use?
**A**: Yes! The entire stack is open-source or free-tier. The only external service is Groq's free API tier.

### Q: What language does FindX understand?
**A**: FindX works best with English questions and English data. The embedding model supports multiple languages, but English is recommended for the best results.

---

## Project Scope & Limitations

### What FindX Can Do ✅
- Answer questions about structured data (spreadsheets, CSVs)
- Find specific records, filter data, and summarize information
- Handle uploads of new files and re-index instantly
- Provide source citations for every answer
- Work offline (except for the Groq API call)

### What FindX Cannot Do ❌
- **Complex calculations**: FindX can find and report data, but it doesn't perform advanced mathematical operations like statistical analysis or chart generation.
- **Real-time database updates**: FindX works with static file uploads, not live database connections.
- **Image/PDF processing**: Currently supports text-based files only (Excel, CSV, TXT). PDF and image support may be added in the future.
- **Multi-user authentication**: The current login is a demo/dummy system. Production deployment would require a real authentication service.
- **Very large files (>100MB)**: While FAISS can handle millions of records, the upload and embedding process for extremely large files may be slow.

---

## Future Roadmap

| Feature | Priority | Description |
|---|---|---|
| PDF Support | High | Parse and index PDF documents |
| Image/OCR Support | Medium | Extract text from images and scanned documents |
| Real Authentication | High | OAuth2/JWT based user management |
| Multi-file Knowledge Base | Medium | Upload and query across multiple files simultaneously |
| Analytics Dashboard | Medium | Charts and graphs for query patterns and data insights |
| Export Answers | Low | Download answers as PDF or share via email |
| Voice Input | Low | Ask questions using voice (speech-to-text) |
| Multi-language Support | Medium | Support for Hindi, Arabic, and other languages |

---

## About the Team

**FindX — AI Based Knowledge Lookup** is a college project developed to demonstrate the practical application of:
- **Retrieval-Augmented Generation (RAG)** — A cutting-edge AI architecture
- **Vector Search** — Using FAISS for semantic similarity
- **Modern Full-Stack Development** — FastAPI backend + responsive frontend
- **Open-Source AI** — Llama 3.1 model via Groq's free API

---

*© 2026 FindX — AI Based Knowledge Lookup. College Project.*
