# Product Requirements Document (PRD)
# Dofus Retro Marketplace Price Analyzer

**Version:** 1.0
**Date:** 2025-11-08
**Project Type:** New Development - Java 26 + Spring Boot
**Based on:** dofus-price-bot-Python (Dofus 2)
**Target Platform:** Dofus Retro

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current System Analysis](#2-current-system-analysis)
3. [Product Vision](#3-product-vision)
4. [Functional Requirements](#4-functional-requirements)
5. [Technical Requirements](#5-technical-requirements)
6. [Architecture & Design](#6-architecture--design)
7. [Data Models](#7-data-models)
8. [API Specifications](#8-api-specifications)
9. [Migration Strategy](#9-migration-strategy)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Future Enhancements](#11-future-enhancements)
12. [Success Metrics](#12-success-metrics)
13. [Risks & Mitigation](#13-risks--mitigation)

---

## 1. Executive Summary

### 1.1 Project Overview

This PRD defines the requirements for building a **Dofus Retro Marketplace Price Analyzer** using Java 26 and Spring Boot. The system will analyze crafting profitability by comparing item prices with their ingredient costs in the Dofus Retro marketplace.

**Key Objective:** Automate marketplace price analysis to determine crafting profitability with minimal manual intervention.

### 1.2 Current System Limitations

The existing Python project (`dofus-price-bot-Python`) has several critical limitations:

| **Limitation** | **Impact** | **Solution for Retro Version** |
|----------------|------------|-------------------------------|
| **NOT packet-based** - Uses OCR screen automation | Unreliable, brittle, requires manual setup | Implement true packet capture or API integration |
| **Dofus 2 data only** - 2,912 equipment recipes | Cannot be used for Dofus Retro | Source Retro-specific recipe database |
| **No database** - Static JSON file | No historical data, no scalability | PostgreSQL/MySQL with JPA entities |
| **Hardcoded screen coordinates** | Breaks with UI changes, resolution differences | Use data-driven approach (packets/API) |
| **Single price point** - No bulk pricing | Inaccurate cost analysis | Capture multiple price tiers |
| **Manual process** - User must select items via GUI | Time-consuming, not scalable | Automated batch analysis |

### 1.3 Strategic Goals

1. **Automation First:** Eliminate manual clicking and OCR-based price reading
2. **Data-Driven:** Build a comprehensive database of recipes, items, and historical prices
3. **Scalable Architecture:** Support future advanced analytics and automation
4. **Dofus Retro Specific:** All data sources and logic tailored to Dofus Retro

---

## 2. Current System Analysis

### 2.1 What the Python Project DOES

Based on comprehensive code analysis, the current system:

**Core Workflow:**
```
User Opens Marketplace
        ↓
[Tkinter GUI] → User selects equipment items to craft
        ↓
For each selected item:
    ↓
[JSON Parser] → Load recipe from equipment_recipes.json
    ↓
For each ingredient:
    ↓
[PyAutoGUI] → Automated clicks to search marketplace
    ↓
[Screenshot] → Capture price region (hardcoded coordinates)
    ↓
[Tesseract OCR] → Extract price from screenshot
    ↓
[Cost Calculator] → Sum ingredient costs + 20% marketplace tax
    ↓
[PrettyTable] → Display results in console
```

**Key Files:**
- `dofus_cookbot/__main__.py` (249 lines) - Core logic: OCR, clicking, calculations
- `dofus_cookbot/gui/gui.py` (153 lines) - Tkinter item selection interface
- `utils/api/api.py` (161 lines) - DofusDB API integration (for data fetching, not live prices)
- `dofus_cookbot/res/equipment_recipes.json` (9.6MB) - 2,912 Dofus 2 equipment recipes

### 2.2 Technologies Used (Python)

```python
# Screen Automation
- PyAutoGUI (mouse/keyboard control)
- Pynput (input simulation)
- Pyscreenshot (screen capture)

# OCR
- Tesseract OCR (text recognition)
- Pillow (image processing)

# UI/Output
- Tkinter (GUI)
- PrettyTable (console tables)

# Data
- JSON (static recipe storage)
- Requests (HTTP API calls to DofusDB)
```

### 2.3 What CAN Be Reused

#### ✅ Reusable Concepts

1. **Recipe Data Structure**
   - Equipment → Ingredients relationship
   - Item properties (name, type, level, quantity)
   - Can be converted to JPA entities

2. **Cost Calculation Logic**
   ```
   Total Cost = Σ(Ingredient Price × Quantity) × (1 + Tax Rate)
   Tax Rate = 20% (Dofus 2, may differ in Retro)
   ```

3. **API Integration Pattern**
   - REST calls to external item databases
   - JSON parsing and mapping
   - Can use Spring WebClient

4. **User Workflow Concept**
   - Browse/search items
   - View crafting cost breakdown
   - Compare crafting vs buying

#### ❌ NOT Reusable

1. **OCR-Based Price Reading** → Replace with packet capture or API
2. **Screen Automation (PyAutoGUI)** → Replace with data-driven approach
3. **Dofus 2 Recipe Data** → Must source Dofus Retro recipes
4. **Tkinter GUI** → Rebuild with JavaFX or Web UI
5. **Hardcoded Coordinates** → Eliminated by new approach

### 2.4 Current Recipe Data Schema

The existing `equipment_recipes.json` structure:

```json
{
  "_id": 14076,
  "name": "Coiffe du Comte Harebourg",
  "type": "Chapeau",
  "imgUrl": "https://s.ankama.com/www/static.ankama.com/dofus/www/game/items/200/16362.png",
  "url": "https://www.dofus.com/fr/mmorpg/encyclopedie/equipements/14076-coiffe-comte-harebourg",
  "description": "Description text...",
  "lvl": "200",
  "stats": [
    {
      "Vitalité": {"from": "451", "to": "500"}
    }
  ],
  "condition": [],
  "recipe": [
    {
      "Galet brasillant": {
        "id": "12740",
        "url": "https://www.dofus-touch.com/fr/mmorpg/encyclopedie/ressources/12740-galet-brasillant",
        "imgUrl": "https://s.ankama.com/www/static.ankama.com/dofus/www/game/items/52/15289.w48h48.png",
        "type": "Galet",
        "lvl": "150",
        "quantity": "3"
      }
    },
    {
      "Ethmoïde du Minotot": {
        "id": "13168",
        "lvl": "160",
        "quantity": "12"
      }
    }
  ],
  "setId": 270
}
```

**Analysis:**
- Equipment has many ingredients (1:N)
- Each ingredient has: id, name, type, level, quantity
- Stats have min/max ranges
- Items can belong to sets

---

## 3. Product Vision

### 3.1 Vision Statement

Build an **automated, data-driven marketplace intelligence system** for Dofus Retro that empowers players to make informed crafting decisions through real-time price analysis, historical trends, and profitability calculations.

### 3.2 Target Users

1. **Crafters/Artisans** - Players who craft items for profit
2. **Merchants** - Players who flip items on the marketplace
3. **Min-Maxers** - Players optimizing resource allocation
4. **Guild Leaders** - Managing guild resources and crafting pipelines

### 3.3 Key User Stories

| **ID** | **User Story** | **Priority** |
|--------|---------------|-------------|
| US-01 | As a crafter, I want to see the total cost to craft an item vs buying it directly, so I can maximize profit | **CRITICAL** |
| US-02 | As a merchant, I want to view historical price trends, so I can identify market opportunities | HIGH |
| US-03 | As a player, I want to search for items by name/level/type, so I can quickly find recipes | **CRITICAL** |
| US-04 | As a crafter, I want to see which ingredients have the highest price volatility, so I can time my purchases | MEDIUM |
| US-05 | As a user, I want automated price updates without manual clicking, so I can save time | **CRITICAL** |
| US-06 | As a merchant, I want to identify undervalued items with low crafting costs, so I can arbitrage | HIGH |
| US-07 | As a guild leader, I want to export cost analyses to CSV, so I can share with guild members | LOW |

### 3.4 Success Criteria

- **Automation:** 0% manual intervention for price retrieval (current: 100% manual)
- **Accuracy:** >95% price data accuracy (current: ~70% due to OCR errors)
- **Coverage:** Support all Dofus Retro craftable items (current: 2,912 Dofus 2 items)
- **Performance:** Price analysis for 100 items in <30 seconds (current: ~10 minutes)
- **Reliability:** System uptime >99% with automated error recovery

---

## 4. Functional Requirements

### 4.1 Core Features (MVP)

#### F-01: Recipe Database Management

**Description:** Store and manage Dofus Retro crafting recipes

**Requirements:**
- Import recipes from Dofus Retro data sources (encyclopedia, APIs, game files)
- Support all crafting professions: Tailor, Jeweler, Smith, Shoemaker, Carver, etc.
- Store item metadata: name, type, level, stats, set affiliation
- Track ingredient relationships: item → ingredients (1:N)
- Support recipe updates/versioning (game patches)

**Acceptance Criteria:**
- ✓ Database contains all Dofus Retro craftable items
- ✓ Recipe data matches in-game recipes (validated manually)
- ✓ System handles recipe updates without data loss

**Current System:** Static JSON file (9.6MB, 2,912 Dofus 2 recipes)
**New System:** PostgreSQL database with JPA entities

---

#### F-02: Marketplace Price Capture

**Description:** Automatically retrieve current marketplace prices for items

**Requirements:**

**CRITICAL DECISION POINT:** Choose price capture strategy:

**Option A: Packet Capture (RECOMMENDED)**
- Intercept Dofus Retro network packets
- Parse marketplace price messages
- Extract: item ID, price, quantity, seller, timestamp
- Libraries: Pcap4J (Java packet capture)

**Option B: Web Scraping**
- Scrape Dofus Retro marketplace websites (if available)
- Parse HTML for price data
- Libraries: Jsoup (Java HTML parser)

**Option C: Crowdsourced Data**
- Users submit prices via web interface
- Validation: cross-reference multiple submissions
- Fallback for Option A/B failures

**Recommended:** Start with **Option A** (packet capture), fallback to **Option C** (crowdsourced)

**Acceptance Criteria:**
- ✓ Prices update automatically (no manual clicking)
- ✓ Capture multiple price points (min, max, average, median)
- ✓ Track bulk discounts (1x, 10x, 100x pricing)
- ✓ Store price timestamps for historical analysis
- ✓ Handle marketplace unavailability gracefully

**Current System:** OCR-based screenshot reading (unreliable)
**New System:** Packet capture or API-based

---

#### F-03: Cost Calculation Engine

**Description:** Calculate total crafting cost and compare with direct purchase price

**Requirements:**
- Input: Item ID or name
- Output: Detailed cost breakdown

**Calculation Formula:**
```
Ingredient Cost = Σ (Ingredient Price × Quantity Required)
Marketplace Tax = Ingredient Cost × Tax Rate (verify Retro tax rate)
Total Crafting Cost = Ingredient Cost + Marketplace Tax
Direct Purchase Price = Current marketplace price for final item
Profit/Loss = Direct Purchase Price - Total Crafting Cost
ROI % = (Profit/Loss) / Total Crafting Cost × 100
```

**Additional Calculations:**
- Cost per stat point (e.g., cost per Vitality point)
- Break-even analysis (at what ingredient prices is crafting profitable?)
- Opportunity cost (time to gather ingredients vs kamas/hour farming)

**Acceptance Criteria:**
- ✓ Accurate cost calculations (validated against manual calculations)
- ✓ Handle missing prices (flag items without price data)
- ✓ Support custom tax rates (configurable per server)
- ✓ Display results in clear, sortable table format

**Current System:** Simple sum + 20% tax
**New System:** Advanced calculations with profitability metrics

---

#### F-04: Item Search & Browse Interface

**Description:** User interface to search and select items for analysis

**Requirements:**

**Interface Options:**
1. **Web UI (RECOMMENDED)** - React/Vue frontend + Spring Boot REST API
2. **JavaFX Desktop App** - Standalone GUI application
3. **CLI** - Command-line interface for power users

**Features:**
- Search by: item name (autocomplete), level range, profession, type
- Filters: only profitable items, minimum ROI %, level range
- Sorting: by profit, ROI %, crafting cost, level
- Batch analysis: select multiple items, analyze all

**Acceptance Criteria:**
- ✓ Autocomplete search returns results in <100ms
- ✓ Filters apply without page reload (SPA behavior)
- ✓ Display item icons, stats, and recipe ingredients
- ✓ One-click cost analysis for any item

**Current System:** Tkinter GUI with search autocomplete
**New System:** Modern web UI or JavaFX

---

#### F-05: Automated Price Updates

**Description:** Periodic background process to refresh marketplace prices

**Requirements:**
- Scheduled task: runs every N minutes (configurable, default: 15 minutes)
- Priority-based updates: high-demand items update more frequently
- Intelligent caching: avoid redundant API/packet calls
- Error handling: retry failed price fetches, log failures
- Notification: alert users when prices change significantly

**Acceptance Criteria:**
- ✓ Prices update automatically without user intervention
- ✓ Update frequency configurable via application.yml
- ✓ Failed updates do not crash the system
- ✓ Users can trigger manual refresh for specific items

**Current System:** None (100% manual)
**New System:** Spring @Scheduled tasks

---

### 4.2 Secondary Features (Post-MVP)

#### F-06: Historical Price Tracking

**Description:** Store and visualize price history over time

**Requirements:**
- Record every price update with timestamp
- Retention policy: keep data for N days (configurable, default: 90 days)
- Analytics: calculate 7-day average, 30-day trend, volatility score
- Visualization: Line charts for price trends over time

**Use Cases:**
- Identify price manipulation or market crashes
- Seasonal price patterns (e.g., weekends vs weekdays)
- Predict future prices using historical trends

**Current System:** None
**New System:** price_history table + charting library (Chart.js, D3.js)

---

#### F-07: Profitability Dashboard

**Description:** Overview of most/least profitable crafts

**Requirements:**
- Top 10 most profitable crafts (highest profit margin)
- Top 10 highest ROI crafts (best return on investment)
- Undervalued items (crafting cost > market price)
- Overvalued items (market price >> crafting cost)
- Filter by profession, level, time investment

**Acceptance Criteria:**
- ✓ Dashboard updates every 15 minutes
- ✓ Displays profit/loss in absolute kamas and % ROI
- ✓ Excludes items with missing price data

**Current System:** None (manual analysis only)
**New System:** Spring Boot backend + dashboard UI

---

#### F-08: Alert System

**Description:** Notify users of price opportunities

**Requirements:**
- User-defined alerts: "Notify me when Item X profit > Y kamas"
- System alerts: "Price of Item X dropped 50% in 1 hour"
- Notification channels: Email, Discord webhook, in-app notification
- Alert history: log all triggered alerts

**Acceptance Criteria:**
- ✓ Alerts trigger within 5 minutes of condition being met
- ✓ Users can create unlimited custom alerts
- ✓ No false positives (validate data before alerting)

**Current System:** None
**New System:** Spring event system + notification service

---

#### F-09: Multi-Server Support

**Description:** Track prices across different Dofus Retro servers

**Requirements:**
- Separate price data per server (e.g., Boune, Eratz)
- User selects default server in settings
- Compare prices across servers (arbitrage opportunities)

**Acceptance Criteria:**
- ✓ Each server has independent price data
- ✓ Users can switch servers without re-login
- ✓ Cross-server price comparison view

**Current System:** Single-server only
**New System:** server_id foreign key in price tables

---

#### F-10: Export & Reporting

**Description:** Export analysis results to various formats

**Requirements:**
- Export formats: CSV, Excel, JSON, PDF
- Custom reports: user selects columns, filters, sorting
- Scheduled reports: email daily profitability summary

**Acceptance Criteria:**
- ✓ Export preserves all data and formatting
- ✓ Large exports (>1000 rows) complete within 30 seconds
- ✓ Reports can be saved as templates

**Current System:** Console output only (PrettyTable)
**New System:** Apache POI (Excel), iText (PDF), Jackson (JSON)

---

## 5. Technical Requirements

### 5.1 Technology Stack

#### Backend

| **Component** | **Technology** | **Version** | **Purpose** |
|---------------|----------------|-------------|-------------|
| **Language** | Java | 26 | Core application language |
| **Framework** | Spring Boot | 3.4+ | Application framework |
| **ORM** | Spring Data JPA | (included) | Database access |
| **Database** | PostgreSQL | 16+ | Primary data store |
| **Caching** | Redis | 7+ | Price data caching |
| **Migration** | Flyway | (included) | Database versioning |
| **Validation** | Hibernate Validator | (included) | Input validation |
| **HTTP Client** | Spring WebFlux | (included) | REST API calls |
| **Packet Capture** | Pcap4J | 1.8+ | Network packet capture (if used) |
| **HTML Parsing** | Jsoup | 1.18+ | Web scraping (if used) |
| **Scheduler** | Spring Scheduler | (included) | Automated tasks |
| **Monitoring** | Spring Actuator | (included) | Health checks |

#### Frontend (If Web UI)

| **Component** | **Technology** | **Purpose** |
|---------------|----------------|-------------|
| **Framework** | React 18+ or Vue 3+ | Modern SPA framework |
| **UI Library** | Tailwind CSS or Material-UI | Styling |
| **Charts** | Chart.js or D3.js | Price trend visualization |
| **HTTP Client** | Axios | API communication |
| **State Management** | Redux or Vuex | Global state |

#### DevOps

| **Component** | **Technology** | **Purpose** |
|---------------|----------------|-------------|
| **Build Tool** | Maven | Dependency management |
| **Testing** | JUnit 5, Mockito | Unit/integration tests |
| **API Docs** | Swagger/OpenAPI | REST API documentation |
| **Logging** | SLF4J + Logback | Application logging |
| **Containerization** | Docker | Deployment packaging (optional) |

---

### 5.2 System Architecture

#### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web UI     │  │  JavaFX GUI  │  │   CLI Tool   │      │
│  │ (React/Vue)  │  │  (Desktop)   │  │   (Maven)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                    REST API (JSON)
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Spring Boot Backend                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Controller Layer                      │  │
│  │  RecipeController  │  PriceController  │  AnalysisCtrl│  │
│  └────────────┬───────────────────────────────────────────┘  │
│               │                                               │
│  ┌────────────┴───────────────────────────────────────────┐  │
│  │                   Service Layer                        │  │
│  │  RecipeService  │  PriceService  │  CostCalculator    │  │
│  │  PacketCapture  │  WebScraper    │  AlertService      │  │
│  └────────────┬───────────────────────────────────────────┘  │
│               │                                               │
│  ┌────────────┴───────────────────────────────────────────┐  │
│  │                Repository Layer (JPA)                  │  │
│  │  RecipeRepo  │  IngredientRepo  │  PriceRepo          │  │
│  └────────────┬───────────────────────────────────────────┘  │
└───────────────┼───────────────────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼────┐  ┌──▼────┐  ┌──▼──────────┐
│ Redis  │  │ PostgreSQL │  │ External APIs│
│ Cache  │  │ Database   │  │ (DofusDB, etc)│
└────────┘  └────────┘  └─────────────┘
```

---

### 5.3 Database Schema Design

#### Core Tables

**Table: `items`**
```sql
CREATE TABLE items (
    id BIGINT PRIMARY KEY,                      -- Dofus Retro item ID
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),                           -- Equipment, Resource, Consumable
    level INTEGER,
    image_url VARCHAR(500),
    description TEXT,
    set_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, level)
);
```

**Table: `recipes`**
```sql
CREATE TABLE recipes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    item_id BIGINT NOT NULL,                    -- FK to items.id (crafted item)
    profession VARCHAR(50) NOT NULL,            -- Tailor, Smith, Jeweler, etc.
    skill_level INTEGER,                        -- Required profession level
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE(item_id)                             -- One recipe per item
);
```

**Table: `recipe_ingredients`**
```sql
CREATE TABLE recipe_ingredients (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recipe_id BIGINT NOT NULL,
    ingredient_id BIGINT NOT NULL,              -- FK to items.id (ingredient)
    quantity INTEGER NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE(recipe_id, ingredient_id)
);
```

**Table: `market_prices`**
```sql
CREATE TABLE market_prices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    item_id BIGINT NOT NULL,
    server VARCHAR(50) NOT NULL,                -- Boune, Eratz, etc.
    price_1x DECIMAL(15, 2),                    -- Price for 1 unit
    price_10x DECIMAL(15, 2),                   -- Price for 10 units (bulk)
    price_100x DECIMAL(15, 2),                  -- Price for 100 units (bulk)
    average_price DECIMAL(15, 2),               -- Average across all quantities
    stock_quantity INTEGER,                     -- Available stock
    recorded_at TIMESTAMP NOT NULL,
    source VARCHAR(50),                         -- packet_capture, api, manual
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    INDEX idx_item_server (item_id, server),
    INDEX idx_recorded_at (recorded_at)
);
```

**Table: `price_history`**
```sql
CREATE TABLE price_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    item_id BIGINT NOT NULL,
    server VARCHAR(50) NOT NULL,
    price DECIMAL(15, 2) NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    INDEX idx_item_time (item_id, recorded_at),
    INDEX idx_server_time (server, recorded_at)
);
```

**Table: `item_stats`** (Optional - for advanced filtering)
```sql
CREATE TABLE item_stats (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    item_id BIGINT NOT NULL,
    stat_name VARCHAR(50) NOT NULL,             -- Vitalité, Force, Agilité, etc.
    stat_min INTEGER,
    stat_max INTEGER,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE(item_id, stat_name)
);
```

**Table: `user_alerts`** (Post-MVP)
```sql
CREATE TABLE user_alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    item_id BIGINT NOT NULL,
    condition_type VARCHAR(50) NOT NULL,        -- profit_threshold, price_drop, etc.
    condition_value DECIMAL(15, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);
```

---

### 5.4 REST API Endpoints

#### Recipe Endpoints

| **Method** | **Endpoint** | **Description** | **Request** | **Response** |
|------------|-------------|----------------|------------|-------------|
| GET | `/api/recipes` | List all recipes | Query params: `profession`, `level`, `name` | `List<RecipeDTO>` |
| GET | `/api/recipes/{id}` | Get recipe details | - | `RecipeDTO` |
| GET | `/api/recipes/{id}/ingredients` | Get recipe ingredients | - | `List<IngredientDTO>` |
| POST | `/api/recipes/import` | Bulk import recipes | `List<RecipeDTO>` | `ImportResultDTO` |

#### Price Endpoints

| **Method** | **Endpoint** | **Description** | **Request** | **Response** |
|------------|-------------|----------------|------------|-------------|
| GET | `/api/prices/item/{itemId}` | Get current price | Query param: `server` | `PriceDTO` |
| GET | `/api/prices/history/{itemId}` | Get price history | Query params: `server`, `days` | `List<PriceHistoryDTO>` |
| POST | `/api/prices/update` | Manual price update | `PriceUpdateDTO` | `PriceDTO` |
| GET | `/api/prices/batch` | Get prices for multiple items | Query param: `itemIds` | `Map<Long, PriceDTO>` |

#### Analysis Endpoints

| **Method** | **Endpoint** | **Description** | **Request** | **Response** |
|------------|-------------|----------------|------------|-------------|
| GET | `/api/analysis/cost/{itemId}` | Calculate crafting cost | Query param: `server` | `CostAnalysisDTO` |
| POST | `/api/analysis/batch` | Analyze multiple items | `List<Long>` (item IDs) | `List<CostAnalysisDTO>` |
| GET | `/api/analysis/profitable` | Top profitable crafts | Query params: `server`, `profession`, `limit` | `List<ProfitabilityDTO>` |
| GET | `/api/analysis/undervalued` | Undervalued items | Query params: `server`, `minDiscount` | `List<ArbitrageDTO>` |

#### Item Search Endpoints

| **Method** | **Endpoint** | **Description** | **Request** | **Response** |
|------------|-------------|----------------|------------|-------------|
| GET | `/api/items/search` | Search items | Query param: `query` | `List<ItemDTO>` |
| GET | `/api/items/{id}` | Get item details | - | `ItemDTO` |
| GET | `/api/items/autocomplete` | Autocomplete suggestions | Query param: `prefix` | `List<String>` |

---

### 5.5 Data Transfer Objects (DTOs)

#### RecipeDTO
```java
public class RecipeDTO {
    private Long itemId;
    private String itemName;
    private String profession;
    private Integer skillLevel;
    private List<IngredientDTO> ingredients;
    private String imageUrl;
}
```

#### IngredientDTO
```java
public class IngredientDTO {
    private Long ingredientId;
    private String name;
    private Integer quantity;
    private Integer level;
    private String type;
}
```

#### PriceDTO
```java
public class PriceDTO {
    private Long itemId;
    private String itemName;
    private String server;
    private BigDecimal price1x;
    private BigDecimal price10x;
    private BigDecimal price100x;
    private BigDecimal averagePrice;
    private Integer stockQuantity;
    private LocalDateTime recordedAt;
    private String source; // packet_capture, api, manual
}
```

#### CostAnalysisDTO
```java
public class CostAnalysisDTO {
    private Long itemId;
    private String itemName;
    private BigDecimal totalCraftingCost;
    private BigDecimal marketplaceTax;
    private BigDecimal totalCostWithTax;
    private BigDecimal currentMarketPrice;
    private BigDecimal profitLoss;
    private BigDecimal roiPercentage;
    private List<IngredientCostDTO> ingredientBreakdown;
    private LocalDateTime calculatedAt;
}
```

#### IngredientCostDTO
```java
public class IngredientCostDTO {
    private String name;
    private Integer quantity;
    private BigDecimal unitPrice;
    private BigDecimal totalCost;
}
```

---

## 6. Architecture & Design

### 6.1 Package Structure

```
com.dofus.retro.analyzer/
├── DofusRetroAnalyzerApplication.java      # Main application
├── config/
│   ├── DatabaseConfig.java
│   ├── CacheConfig.java
│   ├── SecurityConfig.java
│   └── SwaggerConfig.java
├── controller/
│   ├── RecipeController.java
│   ├── PriceController.java
│   ├── AnalysisController.java
│   └── ItemController.java
├── service/
│   ├── RecipeService.java
│   ├── PriceService.java
│   ├── CostCalculatorService.java
│   ├── PacketCaptureService.java           # If using packet capture
│   ├── WebScraperService.java              # If using web scraping
│   └── AlertService.java
├── repository/
│   ├── ItemRepository.java
│   ├── RecipeRepository.java
│   ├── RecipeIngredientRepository.java
│   ├── MarketPriceRepository.java
│   └── PriceHistoryRepository.java
├── domain/                                  # JPA Entities
│   ├── Item.java
│   ├── Recipe.java
│   ├── RecipeIngredient.java
│   ├── MarketPrice.java
│   └── PriceHistory.java
├── dto/
│   ├── RecipeDTO.java
│   ├── IngredientDTO.java
│   ├── PriceDTO.java
│   ├── CostAnalysisDTO.java
│   └── ...
├── mapper/                                  # Entity <-> DTO mapping
│   ├── RecipeMapper.java
│   └── PriceMapper.java
├── exception/
│   ├── ResourceNotFoundException.java
│   ├── PricingException.java
│   └── GlobalExceptionHandler.java
└── scheduler/
    ├── PriceUpdateScheduler.java
    └── AnalyticsScheduler.java
```

---

### 6.2 Key Design Patterns

#### Repository Pattern
```java
@Repository
public interface ItemRepository extends JpaRepository<Item, Long> {
    List<Item> findByNameContainingIgnoreCase(String name);
    List<Item> findByType(String type);
    Optional<Item> findByNameAndLevel(String name, Integer level);
}
```

#### Service Layer Pattern
```java
@Service
public class CostCalculatorService {

    @Autowired
    private RecipeService recipeService;

    @Autowired
    private PriceService priceService;

    public CostAnalysisDTO calculateCraftingCost(Long itemId, String server) {
        Recipe recipe = recipeService.getRecipe(itemId);
        List<RecipeIngredient> ingredients = recipe.getIngredients();

        BigDecimal totalCost = BigDecimal.ZERO;
        List<IngredientCostDTO> breakdown = new ArrayList<>();

        for (RecipeIngredient ingredient : ingredients) {
            PriceDTO price = priceService.getCurrentPrice(
                ingredient.getIngredientId(), server
            );

            BigDecimal ingredientCost = price.getAveragePrice()
                .multiply(BigDecimal.valueOf(ingredient.getQuantity()));

            totalCost = totalCost.add(ingredientCost);
            breakdown.add(new IngredientCostDTO(
                ingredient.getName(),
                ingredient.getQuantity(),
                price.getAveragePrice(),
                ingredientCost
            ));
        }

        // Apply marketplace tax
        BigDecimal tax = totalCost.multiply(new BigDecimal("0.20"));
        BigDecimal totalWithTax = totalCost.add(tax);

        // Get market price for final item
        PriceDTO marketPrice = priceService.getCurrentPrice(itemId, server);

        // Calculate profit/loss
        BigDecimal profitLoss = marketPrice.getAveragePrice().subtract(totalWithTax);
        BigDecimal roi = profitLoss.divide(totalWithTax, 4, RoundingMode.HALF_UP)
            .multiply(BigDecimal.valueOf(100));

        return new CostAnalysisDTO(
            itemId,
            recipe.getItemName(),
            totalCost,
            tax,
            totalWithTax,
            marketPrice.getAveragePrice(),
            profitLoss,
            roi,
            breakdown,
            LocalDateTime.now()
        );
    }
}
```

#### Caching Strategy
```java
@Service
public class PriceService {

    @Cacheable(value = "prices", key = "#itemId + '-' + #server")
    public PriceDTO getCurrentPrice(Long itemId, String server) {
        return marketPriceRepository
            .findLatestPrice(itemId, server)
            .orElseThrow(() -> new PricingException("No price data available"));
    }

    @CacheEvict(value = "prices", allEntries = true)
    public void refreshPriceCache() {
        // Called by scheduler
    }
}
```

#### Scheduled Tasks
```java
@Component
public class PriceUpdateScheduler {

    @Autowired
    private PriceService priceService;

    @Scheduled(fixedDelayString = "${price.update.interval:900000}") // 15 min
    public void updatePrices() {
        log.info("Starting scheduled price update");
        priceService.updateAllPrices();
        log.info("Price update completed");
    }
}
```

---

### 6.3 Packet Capture Architecture (Option A)

If implementing packet capture for price retrieval:

```java
@Service
public class PacketCaptureService {

    private PcapHandle handle;
    private volatile boolean isCapturing = false;

    @PostConstruct
    public void startCapture() throws PcapNativeException {
        PcapNetworkInterface nif = Pcaps.getDevByName("eth0");
        handle = nif.openLive(65536, PromiscuousMode.PROMISCUOUS, 10);

        // Filter for Dofus Retro traffic (adjust port/IP as needed)
        handle.setFilter("tcp port 5555", BpfCompileMode.OPTIMIZE);

        isCapturing = true;

        PacketListener listener = packet -> {
            try {
                processPacket(packet);
            } catch (Exception e) {
                log.error("Error processing packet", e);
            }
        };

        // Run in separate thread
        new Thread(() -> {
            try {
                handle.loop(-1, listener);
            } catch (Exception e) {
                log.error("Packet capture error", e);
            }
        }).start();
    }

    private void processPacket(Packet packet) {
        // Parse Dofus Retro protocol
        // Extract marketplace price messages
        // Example structure (NEEDS REVERSE ENGINEERING):
        // MessageID: 0x1234 (marketplace price update)
        // ItemID: 4 bytes
        // Price: 8 bytes
        // Quantity: 4 bytes

        byte[] payload = packet.getPayload().getRawData();

        // Parse binary protocol (this is example pseudocode)
        int messageId = ByteBuffer.wrap(payload, 0, 2).getShort();

        if (messageId == MARKETPLACE_PRICE_MSG) {
            long itemId = ByteBuffer.wrap(payload, 2, 4).getInt();
            long price = ByteBuffer.wrap(payload, 6, 8).getLong();
            int quantity = ByteBuffer.wrap(payload, 14, 4).getInt();

            // Save to database
            priceService.savePrice(itemId, price, quantity);
        }
    }

    @PreDestroy
    public void stopCapture() {
        if (handle != null && isCapturing) {
            handle.close();
            isCapturing = false;
        }
    }
}
```

**CRITICAL:** Reverse engineering Dofus Retro protocol is required. This involves:
1. Capturing network traffic during marketplace interactions
2. Analyzing packet structure (Wireshark)
3. Identifying message types and data formats
4. Implementing parser for each message type

---

## 7. Data Models

### 7.1 JPA Entity Examples

#### Item Entity
```java
@Entity
@Table(name = "items")
public class Item {

    @Id
    private Long id; // Dofus Retro item ID

    @Column(nullable = false)
    private String name;

    private String type;

    private Integer level;

    @Column(name = "image_url", length = 500)
    private String imageUrl;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "set_id")
    private Integer setId;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @OneToOne(mappedBy = "item", cascade = CascadeType.ALL)
    private Recipe recipe;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // Getters, setters, constructors
}
```

#### Recipe Entity
```java
@Entity
@Table(name = "recipes")
public class Recipe {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    @JoinColumn(name = "item_id", nullable = false, unique = true)
    private Item item;

    @Column(nullable = false)
    private String profession;

    @Column(name = "skill_level")
    private Integer skillLevel;

    @OneToMany(mappedBy = "recipe", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<RecipeIngredient> ingredients = new ArrayList<>();

    // Getters, setters, constructors
}
```

#### RecipeIngredient Entity
```java
@Entity
@Table(name = "recipe_ingredients")
public class RecipeIngredient {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "recipe_id", nullable = false)
    private Recipe recipe;

    @ManyToOne
    @JoinColumn(name = "ingredient_id", nullable = false)
    private Item ingredient;

    @Column(nullable = false)
    private Integer quantity;

    // Getters, setters, constructors
}
```

#### MarketPrice Entity
```java
@Entity
@Table(name = "market_prices", indexes = {
    @Index(name = "idx_item_server", columnList = "item_id, server"),
    @Index(name = "idx_recorded_at", columnList = "recorded_at")
})
public class MarketPrice {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "item_id", nullable = false)
    private Item item;

    @Column(nullable = false)
    private String server;

    @Column(name = "price_1x", precision = 15, scale = 2)
    private BigDecimal price1x;

    @Column(name = "price_10x", precision = 15, scale = 2)
    private BigDecimal price10x;

    @Column(name = "price_100x", precision = 15, scale = 2)
    private BigDecimal price100x;

    @Column(name = "average_price", precision = 15, scale = 2)
    private BigDecimal averagePrice;

    @Column(name = "stock_quantity")
    private Integer stockQuantity;

    @Column(name = "recorded_at", nullable = false)
    private LocalDateTime recordedAt;

    private String source; // packet_capture, api, manual

    // Getters, setters, constructors
}
```

---

## 8. API Specifications

### 8.1 Example API Request/Response

#### GET `/api/analysis/cost/{itemId}`

**Request:**
```
GET /api/analysis/cost/14076?server=Boune
```

**Response (200 OK):**
```json
{
  "itemId": 14076,
  "itemName": "Coiffe du Comte Harebourg",
  "totalCraftingCost": 150000.00,
  "marketplaceTax": 30000.00,
  "totalCostWithTax": 180000.00,
  "currentMarketPrice": 220000.00,
  "profitLoss": 40000.00,
  "roiPercentage": 22.22,
  "ingredientBreakdown": [
    {
      "name": "Galet brasillant",
      "quantity": 3,
      "unitPrice": 10000.00,
      "totalCost": 30000.00
    },
    {
      "name": "Ethmoïde du Minotot",
      "quantity": 12,
      "unitPrice": 5000.00,
      "totalCost": 60000.00
    },
    {
      "name": "Culotte de Harrogant",
      "quantity": 5,
      "unitPrice": 12000.00,
      "totalCost": 60000.00
    }
  ],
  "calculatedAt": "2025-11-08T14:30:00"
}
```

---

### 8.2 Error Handling

**Error Response Format:**
```json
{
  "timestamp": "2025-11-08T14:30:00",
  "status": 404,
  "error": "Not Found",
  "message": "Recipe not found for item ID: 99999",
  "path": "/api/analysis/cost/99999"
}
```

**Global Exception Handler:**
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(ResourceNotFoundException ex) {
        ErrorResponse error = new ErrorResponse(
            LocalDateTime.now(),
            HttpStatus.NOT_FOUND.value(),
            "Not Found",
            ex.getMessage(),
            request.getRequestURI()
        );
        return new ResponseEntity<>(error, HttpStatus.NOT_FOUND);
    }

    @ExceptionHandler(PricingException.class)
    public ResponseEntity<ErrorResponse> handlePricingError(PricingException ex) {
        ErrorResponse error = new ErrorResponse(
            LocalDateTime.now(),
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "Pricing Error",
            ex.getMessage(),
            request.getRequestURI()
        );
        return new ResponseEntity<>(error, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

---

## 9. Migration Strategy

### 9.1 Data Migration from Python Project

The existing Python project uses a static JSON file with Dofus 2 data. Migration steps:

#### Step 1: Extract Dofus Retro Recipe Data

**Options:**

**A. Web Scraping Dofus Retro Encyclopedia**
```java
@Service
public class RetroRecipeScraperService {

    public List<RecipeDTO> scrapeRecipes() {
        List<RecipeDTO> recipes = new ArrayList<>();

        // Example: Scrape from dofus-retro.org encyclopedia
        String baseUrl = "https://www.dofus-retro.org/en/encyclopedia";

        // Get list of craftable items
        Document itemList = Jsoup.connect(baseUrl + "/equipment").get();

        for (Element itemLink : itemList.select(".item-link")) {
            String itemUrl = itemLink.attr("href");
            Document itemPage = Jsoup.connect(baseUrl + itemUrl).get();

            // Extract recipe data
            String itemName = itemPage.select(".item-name").text();
            int itemLevel = Integer.parseInt(itemPage.select(".item-level").text());

            List<IngredientDTO> ingredients = new ArrayList<>();
            for (Element ingredient : itemPage.select(".recipe-ingredient")) {
                String ingName = ingredient.select(".ingredient-name").text();
                int quantity = Integer.parseInt(ingredient.select(".quantity").text());
                ingredients.add(new IngredientDTO(ingName, quantity));
            }

            recipes.add(new RecipeDTO(itemName, itemLevel, ingredients));
        }

        return recipes;
    }
}
```

**B. Manual Data Entry for Critical Items**
- Start with top 100 most-traded items
- Create admin interface for adding recipes
- Community contributions

**C. Dofus Retro Game Files (If Accessible)**
- Extract from client data files
- Reverse engineer game database

#### Step 2: Import to Database

```java
@Service
public class RecipeImportService {

    @Autowired
    private RecipeRepository recipeRepository;

    @Autowired
    private ItemRepository itemRepository;

    @Transactional
    public void importRecipes(List<RecipeDTO> recipeDTOs) {
        for (RecipeDTO dto : recipeDTOs) {
            // Create or find item
            Item item = itemRepository.findByNameAndLevel(dto.getItemName(), dto.getLevel())
                .orElseGet(() -> {
                    Item newItem = new Item();
                    newItem.setName(dto.getItemName());
                    newItem.setLevel(dto.getLevel());
                    newItem.setType(dto.getType());
                    return itemRepository.save(newItem);
                });

            // Create recipe
            Recipe recipe = new Recipe();
            recipe.setItem(item);
            recipe.setProfession(dto.getProfession());

            // Add ingredients
            for (IngredientDTO ingDTO : dto.getIngredients()) {
                Item ingredient = itemRepository.findByName(ingDTO.getName())
                    .orElseGet(() -> {
                        Item newIng = new Item();
                        newIng.setName(ingDTO.getName());
                        return itemRepository.save(newIng);
                    });

                RecipeIngredient recipeIng = new RecipeIngredient();
                recipeIng.setRecipe(recipe);
                recipeIng.setIngredient(ingredient);
                recipeIng.setQuantity(ingDTO.getQuantity());
                recipe.getIngredients().add(recipeIng);
            }

            recipeRepository.save(recipe);
        }
    }
}
```

#### Step 3: Flyway Migration Scripts

**V1__create_initial_schema.sql**
```sql
CREATE TABLE items (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    level INTEGER,
    image_url VARCHAR(500),
    description TEXT,
    set_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, level)
);

CREATE TABLE recipes (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL,
    profession VARCHAR(50) NOT NULL,
    skill_level INTEGER,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE(item_id)
);

-- Additional tables...
```

**V2__import_initial_recipes.sql**
```sql
-- Insert starter data
INSERT INTO items (id, name, type, level) VALUES
(1, 'Petite Epée de Boisaille', 'Épée', 1),
(2, 'Baguette du Boulanger Sombre', 'Bâton', 6);

-- Insert recipes
INSERT INTO recipes (item_id, profession, skill_level) VALUES
(1, 'Forgeron d''Épées', 1);

-- Insert ingredients
-- ...
```

---

## 10. Non-Functional Requirements

### 10.1 Performance

| **Metric** | **Requirement** | **Measurement** |
|------------|----------------|-----------------|
| API Response Time | < 200ms (p95) | Spring Actuator metrics |
| Database Query Time | < 50ms (p95) | Query logging |
| Autocomplete Search | < 100ms | Browser DevTools |
| Batch Analysis (100 items) | < 30 seconds | Load testing |
| Price Update Frequency | Every 15 minutes | Scheduler logs |
| Concurrent Users | Support 100+ | JMeter load tests |

### 10.2 Scalability

- **Horizontal Scaling:** Stateless Spring Boot instances behind load balancer
- **Database Scaling:** Read replicas for query-heavy operations
- **Caching:** Redis for frequently accessed price data
- **Async Processing:** CompletableFuture for batch operations

### 10.3 Reliability

- **Uptime:** 99% availability
- **Data Integrity:** Database constraints, foreign keys, transactions
- **Error Recovery:** Retry logic for external API calls (3 retries with exponential backoff)
- **Graceful Degradation:** If price data unavailable, show last known price with timestamp

### 10.4 Security

- **Input Validation:** Hibernate Validator on all DTOs
- **SQL Injection Prevention:** JPA/JDBC parameterized queries
- **Rate Limiting:** Max 100 requests/minute per IP (Spring Security)
- **CORS:** Whitelist frontend domain only
- **(Optional) Authentication:** JWT tokens for user-specific features (alerts, saved searches)

### 10.5 Maintainability

- **Code Coverage:** Minimum 70% unit test coverage
- **Documentation:** Swagger UI for API docs, JavaDoc for complex methods
- **Logging:** SLF4J with structured logging (JSON format)
- **Monitoring:** Spring Actuator health checks, Prometheus metrics

---

## 11. Future Enhancements

### 11.1 Phase 2 Features

1. **Machine Learning Price Predictions**
   - Train model on historical price data
   - Predict future prices based on trends
   - Identify anomalies (price manipulation)

2. **Crafting Optimizer**
   - Given X kamas and profession level, recommend most profitable crafts
   - Multi-step crafting (craft ingredients first if cheaper)

3. **Marketplace Arbitrage Detector**
   - Identify buy-low-sell-high opportunities
   - Cross-server price differences
   - Seasonal patterns (weekend vs weekday)

4. **Resource Gathering Planner**
   - Show which resources can be gathered vs bought
   - Calculate time vs kamas trade-off
   - Map locations for gathering resources

5. **Guild Crafting Coordinator**
   - Multi-user access with role-based permissions
   - Shared crafting queues
   - Resource pooling across guild members

### 11.2 Advanced Analytics

1. **Market Sentiment Analysis**
   - Track price velocity (how fast prices change)
   - Volume analysis (high demand items)
   - Volatility score (risk indicator)

2. **Profitability Heatmaps**
   - Visual dashboard showing profitability by profession
   - Filter by player level, capital available

3. **Supply Chain Analysis**
   - Multi-level ingredient trees
   - Identify bottleneck ingredients (low supply, high demand)

---

## 12. Success Metrics

### 12.1 Technical Metrics

| **KPI** | **Target** | **Tracking Method** |
|---------|-----------|---------------------|
| API Uptime | 99%+ | Actuator health checks |
| Average Response Time | < 200ms | Prometheus metrics |
| Price Data Accuracy | > 95% | Manual validation samples |
| Test Coverage | > 70% | JaCoCo reports |
| Database Query Performance | < 50ms | Hibernate query logging |

### 12.2 Business Metrics

| **KPI** | **Target** | **Tracking Method** |
|---------|-----------|---------------------|
| Daily Active Users | 50+ (within 3 months) | Analytics |
| Price Analyses Performed | 1000+/day | Database logs |
| User Retention (30-day) | 40%+ | User analytics |
| Recipe Coverage | 80% of craftable items | Database count vs game data |

### 12.3 User Satisfaction

- **User Feedback:** In-app feedback form, Discord community
- **Feature Requests:** Public roadmap, voting system
- **Bug Reports:** GitHub Issues integration

---

## 13. Risks & Mitigation

### 13.1 Technical Risks

| **Risk** | **Probability** | **Impact** | **Mitigation** |
|----------|----------------|-----------|----------------|
| **Dofus Retro protocol reverse engineering fails** | HIGH | CRITICAL | Fallback to web scraping or crowdsourced data |
| **No public Retro API available** | MEDIUM | HIGH | Build web scraper, manual data entry |
| **Packet capture blocked by game client** | MEDIUM | HIGH | Use alternative data sources (APIs, scraping) |
| **Price data becomes stale** | LOW | MEDIUM | Alerting system for stale data, manual overrides |
| **Database performance degrades** | LOW | MEDIUM | Indexing, query optimization, caching |

### 13.2 Legal/Compliance Risks

| **Risk** | **Probability** | **Impact** | **Mitigation** |
|----------|----------------|-----------|----------------|
| **Violation of Dofus ToS** | MEDIUM | HIGH | Review Ankama's ToS, avoid modifying game client |
| **Packet capture legal issues** | LOW | MEDIUM | Capture only local traffic, no MITM attacks |
| **Copyright issues (recipe data)** | LOW | LOW | Use publicly available data, attribute sources |

**Legal Disclaimer:**
> This tool is for educational and informational purposes. Users are responsible for compliance with Dofus Retro Terms of Service. The developers do not encourage or condone violation of game rules.

### 13.3 Operational Risks

| **Risk** | **Probability** | **Impact** | **Mitigation** |
|----------|----------------|-----------|----------------|
| **Game updates break data sources** | HIGH | HIGH | Version detection, automated testing, manual fallback |
| **Server-specific price differences** | MEDIUM | MEDIUM | Multi-server support from day 1 |
| **User-submitted data spam/abuse** | MEDIUM | LOW | Rate limiting, validation, moderation tools |

---

## 14. Development Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Week 1-2: Data Layer**
- [ ] Set up Spring Boot project (Java 26, Maven)
- [ ] Configure PostgreSQL database
- [ ] Create JPA entities (Item, Recipe, RecipeIngredient, MarketPrice)
- [ ] Write Flyway migration scripts
- [ ] Implement repositories
- [ ] Source Dofus Retro recipe data (scraping or manual)
- [ ] Import initial recipe dataset

**Week 3-4: Core Business Logic**
- [ ] Implement RecipeService, PriceService
- [ ] Build CostCalculatorService with tax calculations
- [ ] Create REST API controllers
- [ ] Write unit tests (JUnit 5, Mockito)
- [ ] Set up Swagger API documentation

### Phase 2: Price Capture (Weeks 5-8)

**Week 5-6: Price Data Source**
- [ ] Research Dofus Retro protocol (Wireshark analysis)
- [ ] Implement packet capture service (Pcap4J) OR
- [ ] Build web scraper (Jsoup) OR
- [ ] Create manual price submission API
- [ ] Test price capture accuracy

**Week 7-8: Automation**
- [ ] Implement scheduled price updates (@Scheduled)
- [ ] Add Redis caching for prices
- [ ] Build batch price retrieval
- [ ] Error handling and retry logic

### Phase 3: Frontend (Weeks 9-12)

**Week 9-10: UI Development**
- [ ] Choose frontend: React/Vue web app OR JavaFX desktop
- [ ] Implement item search with autocomplete
- [ ] Build cost analysis display page
- [ ] Create profitability dashboard

**Week 11-12: Polish**
- [ ] Add price history charts
- [ ] Implement filters and sorting
- [ ] Mobile responsive design (if web)
- [ ] User settings (default server, tax rate)

### Phase 4: Advanced Features (Weeks 13-16)

**Week 13-14: Analytics**
- [ ] Historical price tracking
- [ ] Profitability rankings
- [ ] Undervalued items detector
- [ ] Export to CSV/Excel

**Week 15-16: Launch Prep**
- [ ] Load testing and performance optimization
- [ ] Security audit
- [ ] User documentation (README, tutorials)
- [ ] Beta testing with Dofus Retro community

### Phase 5: Post-Launch (Ongoing)

- [ ] Monitor usage metrics
- [ ] Fix bugs based on user feedback
- [ ] Add new features from Phase 2 roadmap
- [ ] Expand recipe coverage

---

## 15. Conclusion

### 15.1 Summary

This PRD defines a comprehensive plan to rebuild the Python Dofus 2 price bot as a **modern, automated, data-driven marketplace analyzer for Dofus Retro** using Java 26 and Spring Boot.

**Key Improvements Over Current System:**
1. **Automated** - No manual clicking or OCR (packet capture or API-based)
2. **Reliable** - Database-backed with error handling and caching
3. **Scalable** - REST API, horizontal scaling, microservices-ready
4. **Feature-Rich** - Historical trends, profitability analytics, alerts
5. **Maintainable** - Clean architecture, comprehensive tests, documentation

### 15.2 Next Steps

1. **Validate Technical Approach** - Confirm Dofus Retro protocol can be captured/parsed
2. **Source Recipe Data** - Identify and scrape Dofus Retro recipe sources
3. **Set Up Development Environment** - Java 26, Spring Boot, PostgreSQL
4. **Start Phase 1 Implementation** - Begin with data layer and core services

### 15.3 Open Questions

1. **What is the exact Dofus Retro marketplace tax rate?** (assumed 20% like Dofus 2)
2. **Are there public Dofus Retro APIs for recipe/item data?**
3. **Does packet capture work with Dofus Retro client?** (needs testing)
4. **Which Retro servers to support?** (Boune, Eratz, etc.)
5. **User authentication required?** (if adding user-specific features like alerts)

---

## Appendix A: Comparison Matrix

| **Feature** | **Python Project (Current)** | **Java/Spring Boot (Proposed)** |
|-------------|------------------------------|----------------------------------|
| **Price Capture** | OCR (unreliable) | Packet capture or API (reliable) |
| **Data Storage** | Static JSON (9.6MB) | PostgreSQL (scalable) |
| **Automation** | 0% (manual clicking) | 100% (scheduled tasks) |
| **Historical Data** | None | Price history table |
| **API** | None | REST API with Swagger docs |
| **UI** | Tkinter (basic) | Web UI or JavaFX (modern) |
| **Scalability** | Single-user | Multi-user, horizontally scalable |
| **Testing** | None | JUnit 5, >70% coverage |
| **Caching** | None | Redis |
| **Analytics** | Basic cost sum | Advanced profitability, ROI, trends |
| **Game Version** | Dofus 2 | Dofus Retro |
| **Recipe Count** | 2,912 (Dofus 2) | TBD (Retro-specific) |

---

## Appendix B: Technology Decision Matrix

| **Decision** | **Options Considered** | **Chosen** | **Rationale** |
|--------------|------------------------|-----------|---------------|
| **Backend Language** | Java, Kotlin, Scala | Java 26 | User requirement |
| **Framework** | Spring Boot, Quarkus, Micronaut | Spring Boot | Mature ecosystem, extensive docs |
| **Database** | PostgreSQL, MySQL, MongoDB | PostgreSQL | Strong relational model, JSON support |
| **Caching** | Redis, Hazelcast, Caffeine | Redis | Industry standard, easy Spring integration |
| **ORM** | Hibernate (JPA), jOOQ, JDBC | JPA (Hibernate) | Spring Data JPA convenience |
| **Frontend** | React, Vue, Angular, JavaFX | TBD | Depends on deployment model (web vs desktop) |
| **Price Capture** | Packet capture, Web scraping, Manual | Packet capture + Manual fallback | Most automated, with safety net |
| **Testing** | JUnit 5, TestNG | JUnit 5 | Spring Boot default |
| **Build Tool** | Maven, Gradle | Maven | User requirement (standard for Java) |

---

## Appendix C: Sample Configuration

**application.yml**
```yaml
spring:
  application:
    name: dofus-retro-analyzer

  datasource:
    url: jdbc:postgresql://localhost:5432/dofus_retro
    username: dofus_user
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 10

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate:
        format_sql: true

  flyway:
    enabled: true
    baseline-on-migrate: true

  cache:
    type: redis

  redis:
    host: localhost
    port: 6379

dofus:
  retro:
    default-server: Boune
    marketplace-tax-rate: 0.20
    price:
      update-interval: 900000 # 15 minutes in ms
      cache-ttl: 3600 # 1 hour in seconds
    packet-capture:
      enabled: true
      network-interface: eth0
      port: 5555

logging:
  level:
    com.dofus.retro: DEBUG
    org.springframework.web: INFO
    org.hibernate.SQL: DEBUG

management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
```

---

**END OF PRD**

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Author:** Generated based on dofus-price-bot-Python analysis
**Status:** Draft - Awaiting Review

