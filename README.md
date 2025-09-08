# Network Impact Analysis Tool

## Overview
The Network Impact Analysis Tool is a web-based application that analyzes the impact of node or exchange failures on network infrastructure. It provides both data analysis and visualizations to help network engineers understand potential failure scenarios.

## Features
- Node and exchange failure impact analysis
- Interactive network topology visualization
- Data filtering and pagination
- Impact summary statistics and charts
- Export functionality for analysis results
- Support for both WE and Others network data types
- Network Path Impact Analysis Dashboard

## Data Requirements
Place the following CSV files in the data directory:

- Report(11).csv (WE data)
- Report(12).csv (Others data)
- res_ospf.csv
- wan.csv
- agg.csv

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd network-impact-analysis
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Install required JavaScript libraries (they are loaded via CDN in the HTML):
- Chart.js (for charts)
- D3.js (for network visualization)

## Usage
1. Start the backend API server:
    - python main_API.py

2. Start the web interface server:
    - python main.py

3. Open your browser and navigate to:
    http://localhost:8001

## Project Structure
```bash
network-impact-analysis/
├── main_API.py # Backend API server
├── main.py # Web interface server
├── unified_network_analyzer.py # Core analysis logic
├── static/
│ ├── style.css # Stylesheet
│ ├── script.js # Client-side JavaScript
│ ├── dashboard.css # Dshboard Stylesheet
│ └── dashboard.js # Dashboard JavaScript
├── templates/
│ ├── index.html # Home page template
│ └── results.html # Results page template
├── data/ # Data files directory
└── README.md # This file
```