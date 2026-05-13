# Project North Star

## Title

**A Multi-Level Media Authenticity Verification Framework Using AI-Based Deepfake Detection and Blockchain Provenance**

## 1. Vision

This project is **not** a generic deepfake detector.

It is a research-oriented, explainable, multi-layer authenticity verification framework that demonstrates how deterministic provenance checks and probabilistic AI analysis can complement each other in digital media authentication.

The system should feel like:

- a digital forensics tool
- a provenance verification platform
- an educational blockchain-security demonstration
- a transparent media authenticity laboratory

The user experience should resemble transparent blockchain visualizations, similar in spirit to educational blockchain demos by Anders Brownworth.

The project must prioritize:

- explainability
- transparency
- layered verification
- clean architecture
- research credibility

The project must **not** feel like:

- a generic AI classifier
- a SaaS dashboard
- a social media app
- an enterprise blockchain product

## 2. Research Problem

Deepfake technology and AI-generated synthetic media are rapidly eroding trust in digital content.

Existing systems commonly suffer from one or more limitations:

- AI-only detection approaches are unreliable and often fail to generalize
- blockchain-only systems verify integrity but cannot detect semantic manipulation
- many systems provide binary outputs such as "real" or "fake"
- transparency and interpretability are often weak
- provenance information is frequently inaccessible or difficult to verify

Research in digital media authentication consistently highlights:

- poor generalization of deepfake detectors
- lack of explainability
- need for provenance verification
- importance of layered verification approaches

This project addresses those gaps by combining:

- blockchain provenance
- metadata analysis
- AI-assisted deepfake detection
- explainable trust scoring

## 3. Research Question

Can a multi-level verification framework combining blockchain provenance, metadata integrity analysis, and AI-based deepfake detection improve the reliability and interpretability of digital media authentication?

## 4. Core Contribution

The novelty of this project is **not**:

- inventing blockchain
- inventing deepfake detection
- creating a new AI architecture

The novelty **is**:

- combining multiple verification layers into one framework
- generating an explainable trust score
- visualizing transparent provenance data
- integrating deterministic and probabilistic verification
- improving interpretability in authenticity verification

The system should consistently be described as:

> An explainable multi-layer authenticity verification framework.

It should **not** be described as:

> A deepfake detector.

## 5. Technical Philosophy

This project is a prototype, proof of concept, and research demonstration system.

It must prioritize:

- feasibility
- explainability
- clarity
- demonstrability
- modularity
- educational transparency

It is **not**:

- production-ready infrastructure
- real-time enterprise infrastructure
- a replacement for professional forensic systems

## 6. Scope

### Must Do

- image-based verification
- SHA-256 hashing
- blockchain provenance registration
- metadata analysis
- AI-based authenticity scoring
- trust-score generation
- interactive web interface
- transparent verification pipeline visualization

### Optional

- short video support
- improved metadata analysis
- enhanced provenance explorer
- visual trust analytics

### Must Not Do

- train deep learning models from scratch
- support large-scale video processing
- use Ethereum mainnet
- store media files on-chain
- claim perfect deepfake detection
- claim production security
- implement decentralized storage systems
- build custom blockchain infrastructure

## 7. High-Level Architecture

```text
User Upload
     |
     v
SHA-256 Hash Engine
     |
     v
Blockchain Provenance Layer
     |
     v
Metadata Analysis Layer
     |
     v
AI Authenticity Analysis Layer
     |
     v
Trust Score Engine
     |
     v
Verification Report UI
```

## 8. System Modules

### 8.1 Media Registration Module

**Purpose:** Register authentic or original media.

**Responsibilities:**

- upload media
- generate SHA-256 hash
- generate timestamp
- store provenance on blockchain
- create provenance record

**Outputs:**

- media hash
- transaction ID
- timestamp
- provenance certificate

### 8.2 Blockchain Provenance Module

**Purpose:** Provide immutable provenance records.

**Implementation constraints:**

- use a local blockchain only
- use Ganache as the test blockchain
- use Solidity smart contracts
- use Web3.py integration

**Blockchain stores only:**

- media hash
- timestamp
- owner identifier
- provenance metadata

**Blockchain must not store:**

- media content
- images
- videos

### 8.3 Metadata Analysis Module

**Purpose:** Perform forensic consistency analysis.

Checks may include:

- EXIF consistency
- creation timestamp consistency
- editing software traces
- metadata completeness
- recompression indicators
- format inconsistencies

This module contributes to:

- trust scoring
- explainability
- forensic transparency

### 8.4 AI Authenticity Analysis Module

**Purpose:** Estimate manipulation likelihood.

**Implementation rules:**

- use pretrained models only
- run inference only
- keep the architecture lightweight
- prioritize compatibility with macOS

Do **not**:

- train large models
- use CUDA-dependent pipelines
- use heavy transformer architectures

Preferred approach:

- lightweight CNN models
- image-based deepfake detection
- local inference

**Outputs:**

- authenticity probability
- manipulation confidence
- suspicion indicators

### 8.5 Trust Score Engine

**Purpose:** Combine verification layers into interpretable authenticity scoring.

This is the intellectual center of the project.

Suggested weighting:

| Layer | Weight |
| --- | ---: |
| Blockchain provenance | 40% |
| AI authenticity analysis | 40% |
| Metadata integrity | 20% |

Example output:

| Verification Layer | Result |
| --- | --- |
| Blockchain Verification | PASS |
| Metadata Integrity | PARTIAL |
| AI Authenticity | 78% |
| Final Trust Score | 84% |

The trust score must:

- be explainable
- show contributing factors
- avoid black-box outputs

## 9. User Experience Philosophy

The application should feel:

- forensic
- transparent
- investigative
- educational
- interactive

The UI should expose:

- hashes
- timestamps
- block information
- verification stages
- trust-score calculations

Avoid:

- minimal AI-only interfaces
- generic dashboards
- hidden processing

## 10. Demo Flow

### Step 1: Register Authentic Media

The user uploads an original image.

The system:

- generates a hash
- stores provenance
- creates a blockchain transaction

The UI shows:

- hash
- block number
- timestamp
- transaction confirmation

### Step 2: Verify Original Media

Expected result:

- blockchain match
- high metadata integrity
- high authenticity score
- high trust score

### Step 3: Verify Manipulated Media

Expected result:

- hash mismatch
- metadata anomalies
- lower AI confidence
- reduced trust score

### Step 4: Display Transparent Verification Report

Example report:

| Verification Layer | Result |
| --- | --- |
| Blockchain Provenance | VERIFIED |
| Metadata Integrity | SUSPICIOUS |
| AI Authenticity | 76% |
| Final Trust Score | 81% |

This transparency is essential.

## 11. Evaluation Philosophy

Evaluation must align with the claimed contribution.

The project should be evaluated on:

- interpretability
- layered verification effectiveness
- trust-score consistency
- prototype usability
- verification transparency

It should **not** be evaluated solely on raw AI accuracy.

## 12. Evaluation Metrics

### AI Metrics

- accuracy
- precision
- recall
- F1-score

### System Metrics

- verification latency
- blockchain lookup time
- hash generation time
- transaction confirmation time

### Framework Metrics

- trust-score consistency
- tamper detection rate
- provenance verification success rate

## 13. Required Test Cases

### Test Case 1: Authentic Registered Image

Expected result:

- hash match
- valid provenance
- high trust score

### Test Case 2: Edited Image

Examples:

- cropped image
- brightness-adjusted image
- filtered image
- recompressed image

Expected result:

- hash mismatch
- metadata inconsistencies
- reduced trust score

### Test Case 3: Deepfake Image

Expected result:

- suspicious AI output
- missing provenance
- low trust score

### Test Case 4: Unknown Image

Expected result:

- no provenance record
- unverified authenticity

## 14. Technology Constraints

### Backend

- Python Flask preferred

### Blockchain

- Ganache
- Solidity
- Hardhat
- Web3.py

### AI

- TensorFlow or PyTorch
- lightweight pretrained model
- macOS-compatible inference

### Metadata

- Pillow
- exifread

### Frontend

Prioritize:

- transparency
- visual verification flow
- provenance exploration

## 15. macOS Compatibility

The project must remain compatible with macOS development environments.

Avoid:

- CUDA dependencies
- Linux-only tooling
- GPU-heavy architectures

Optimize for:

- Apple Silicon compatibility
- lightweight local inference
- manageable resource usage

## 16. Coding Principles

The codebase must prioritize:

- modularity
- readability
- separation of concerns
- explainability
- deterministic verification flow

Modules should remain independently testable.

Avoid:

- monolithic architecture
- tightly coupled logic
- hidden processing

## 17. Research Positioning

The system should be positioned academically as:

- a prototype framework
- a proof-of-concept architecture
- a layered verification system
- an explainable authenticity verification pipeline

Avoid claiming:

- perfect detection
- universal generalization
- complete security guarantees

Use wording such as:

- "assists authenticity verification"
- "improves interpretability"
- "enhances provenance transparency"
- "provides layered verification"

## 18. Literature-Grounded Positioning

The project aligns with current concerns in:

- digital provenance
- explainable AI
- media authenticity
- deepfake mitigation
- blockchain-backed verification systems

Research repeatedly highlights:

- need for provenance systems
- importance of explainability
- limitations of AI-only detection
- importance of hybrid verification frameworks

## 19. Final North Star

The final system should feel like:

> A transparent digital forensics and authenticity verification laboratory demonstrating how blockchain provenance and AI-assisted analysis can work together to restore trust in digital media.
