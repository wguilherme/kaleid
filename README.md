# Kaleid

## 📚 About
Kaleid is a sophisticated data collection and processing tool designed to help users navigate and consume the vast amount of digital content available today. By automating the collection, processing, and organization of content from various sources, Kaleid makes information consumption more efficient and manageable.

## 🎯 Features
- **Multi-source Data Collection**: Collects data from:
  - RSS News Feeds
  - Cryptocurrency Market Data
  - (Expandable to other sources)
- **Automated Processing**: Standardizes and organizes collected data
- **Structured Output**: Saves processed data in JSON format with timestamps
- **Modular Architecture**: Easily extendable for new data sources

## 🛠️ Technical Architecture
- **Base DataSource**: Abstract class that defines the interface for all data sources
- **Specialized Collectors**: Implementation for specific data types (RSS, Crypto, etc.)
- **Central Collector**: Manages and orchestrates all data collection processes

## 🚀 Getting Started

### Prerequisites
- Docker
- Docker Compose
- Make

### Configuration
Create a config.json file:
```json
{
  "gpt_api_key": "your_api_key",
  "sources": [
    {
      "type": "rss",
      "url": "https://feeds.feedburner.com/TechCrunch/",
      "name": "TechCrunch"
    },
    {
      "type": "crypto",
      "url": "https://api.coingecko.com/api/v3/simple/price",
      "symbol": "BTC"
    }
  ]
}
```

### Running the application

```bash
# Start the application
make up

# View logs in real-time
make logs
```


## 📂 Project Structure

```bash
kaleid/
├── sources/
│   ├── base.py
│   ├── news.py
│   └── crypto.py
├── collector.py
├── config.json
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## 🔄 Data Flow

Configuration loaded
DataCollector initializes source-specific collectors
Data is fetched from each source
Raw data is processed and standardized
Processed data is saved with timestamps

## 🛣️ Roadmap

 Add more data sources
 Implement data analytics
 Create web interface
 Add content summarization
 Implement user preferences

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.