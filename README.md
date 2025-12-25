# ⚡ EVChargeAdvisor-AI

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Global](https://img.shields.io/badge/coverage-200%2B%20countries-brightgreen)

**AI-Enhanced EV Charging Infrastructure Equity Analysis System**

A premium, enterprise-level tool for analyzing electric vehicle charging infrastructure through the lens of equity, accessibility, and sustainability. Works globally with real-time data.

![EVChargeAdvisor-AI Screenshot](docs/screenshot.png)

## ✨ Features

### 🌍 Global Coverage
- Works in **200+ countries** worldwide
- Real-time data from OpenChargeMap
- US Census data for USA, World Bank for other countries

### 📊 Comprehensive Analysis
- **Infrastructure Analysis**: Station coverage, operator distribution, charging levels
- **Equity Assessment**: Demographic analysis, income-based access, poverty correlation
- **Accessibility Scoring**: Convenience metrics, transit access, amenity proximity
- **Climate Impact**: Weather effects on EV range

### 🤖 AI-Powered Insights
- LLM-generated analysis using Groq (Llama 3.3 70B)
- Interactive AI chat for Q&A
- Policy recommendations
- Infrastructure gap analysis

### 📈 Advanced Features
- **Station Finder**: Search and filter charging stations
- **Gap Finder**: AI identifies optimal locations for new stations
- **Cost Calculator**: Compare EV charging vs gasoline costs
- **Export Reports**: Download analysis in TXT, CSV, JSON formats
- **Interactive Maps**: 4 map types (stations, heatmap, operator, coverage)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- API keys (free):
  - [OpenChargeMap](https://openchargemap.org/site/developerinfo)
  - [US Census Bureau](https://api.census.gov/data/key_signup.html)
  - [Groq](https://console.groq.com/)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/EVChargeAdvisor-AI.git
cd EVChargeAdvisor-AI
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API keys**
```bash
cp config/api_keys_template.py config/api_keys.py
# Edit config/api_keys.py and add your API keys
```

4. **Run the application**
```bash
streamlit run streamlit_app/app.py
```

5. **Open in browser**
```
http://localhost:8501
```

## 📁 Project Structure
```
EVChargeAdvisor-AI/
├── config/
│   ├── api_keys.py          # API keys (not in repo)
│   ├── api_keys_template.py # Template for API keys
│   └── settings.py          # App settings
├── src/
│   ├── data_access/         # API clients
│   │   ├── base_api.py
│   │   ├── openchargemap.py
│   │   ├── census_client.py
│   │   ├── worldbank_api.py
│   │   ├── overpass_api.py
│   │   ├── weather_api.py
│   │   └── groq_api.py
│   ├── analysis/            # Analysis modules
│   │   ├── infrastructure_analyzer.py
│   │   ├── equity_analyzer.py
│   │   ├── global_equity_analyzer.py
│   │   └── accessibility_analyzer.py
│   └── visualization/       # Charts and maps
│       ├── map_visualizer.py
│       └── chart_generator.py
├── streamlit_app/
│   ├── app.py               # Main Streamlit app
│   └── components/          # UI components
├── data/                    # Data storage
├── docs/                    # Documentation
├── tests/                   # Unit tests
├── requirements.txt
├── README.md
└── .gitignore
```

## 🌐 Supported Locations

### Pre-configured Cities
- 🇺🇸 San Francisco, Los Angeles, New York (USA)
- 🇬🇧 London (UK)
- 🇩🇪 Berlin (Germany)
- 🇫🇷 Paris (France)
- 🇯🇵 Tokyo (Japan)
- 🇨🇳 Shanghai (China)
- 🇹🇭 Bangkok (Thailand)
- 🇸🇬 Singapore
- 🇦🇺 Sydney (Australia)
- 🇮🇳 Mumbai (India)
- 🇧🇷 São Paulo (Brazil)
- 🇿🇦 Cape Town (South Africa)

### Custom Locations
Enter any coordinates to analyze any location worldwide!

## 📊 Data Sources

| Source | Coverage | Data Type |
|--------|----------|-----------|
| OpenChargeMap | Global | EV charging stations |
| US Census Bureau | USA | Demographics (county-level) |
| World Bank | Global | Demographics (country-level) |
| OpenStreetMap | Global | Amenities, transit |
| Open-Meteo | Global | Weather, climate |
| Groq LLM | - | AI analysis |

## 🎯 Use Cases

- **Urban Planners**: Identify infrastructure gaps and optimal locations
- **Policy Makers**: Assess equity in charging access
- **Researchers**: Analyze EV adoption patterns
- **EV Owners**: Find charging stations and estimate costs
- **Investors**: Evaluate market opportunities

## 📝 Citation

If you use this tool in your research, please cite:
```bibtex
@software{evchargeadvisor2024,
  author = {MAHBUB},
  title = {EVChargeAdvisor-AI: AI-Enhanced EV Charging Infrastructure Equity Analysis},
  year = {2024},
  institution = {Chulalongkorn University},
  url = {https://github.com/yourusername/EVChargeAdvisor-AI}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**MAHBUB**  
Transportation Research  
Chulalongkorn University  
Email: 6870376421@student.chula.ac.th

## 🙏 Acknowledgments

- OpenChargeMap for charging station data
- US Census Bureau for demographic data
- World Bank for global economic data
- OpenStreetMap for amenity data
- Groq for LLM API access

---

<p align="center">
  Made with ❤️ for sustainable transportation
</p>