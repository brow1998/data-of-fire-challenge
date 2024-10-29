# Data of Fire - Data Engineer Challenge

## Description

This project was developed to analyze fire incident data in San Francisco, enabling the Business Intelligence (BI) team to run dynamic queries aggregated by time period, district, and battalion. The solution simulates a data warehouse that reflects the current state of data from the source, with daily updates.

## Architecture

The project uses:

* **PostgreSQL** as a simulated data warehouse for data storage and querying.
* **Metabase** for data visualization and reporting.
* **Docker** to orchestrate the database and BI environments.
* **Python** to automate data extraction and preprocessing.

## Directory Structure

```
.
├── .deploy                  # Persistent Docker data for PostgreSQL and Metabase
├── config                   # Configuration files
├── data/raw                 # Raw daily incident data in CSV
├── scripts                  # Python extraction script
├── sql                      # SQL scripts for data warehouse table creation and ingestion
├── docker-compose.yml       # Docker configuration
└── README.md                # Documentation
```

## Setup and Execution

### Prerequisites

* **Docker** and **Docker Compose** installed locally.

### Execution Instructions

1. Clone this repository and navigate to the directory.
2. Start the services with Docker Compose:

   `docker-compose up -d`
3. Run the data extraction script:

   `python scripts/extract.py`

   This script will:

   * Download the latest dataset.
   * Transform and clean the data.
   * Insert the data into PostgreSQL for analysis.
4. Access Metabase at [http://localhost:3000]() to view reports and run queries.

   - The user should be Admin / brow1998@gmail.com and the password Admin2024.

### SQL for Modeling and Queries

The SQL files in the `sql` folder include:

* `create_tables.sql` - Creates the necessary tables in PostgreSQL.
* `ingestion_to_dw.sql` - Ingests the transformed data into the `fire_incidents` table for analysis.

*Note: DBT was not used due to the 2-hour time constraint, so SQLs were run directly on the database.*

## Sample Report

A basic report in Metabase shows incidents aggregated by battaliion and Day of Week, enabling the BI team to explore patterns and trends in incidents.
