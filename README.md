# AI-Powered Loan Underwriting System with MCP and A2A Protocol
An intelligent loan underwriting system that leverages AI agents communicating through Agent-to-Agent (A2A) protocol, built with Model Context Protocol (MCP) using FastMCP framework.

## 🌟 Features
- **Dual Agent Architecture**: DataFetcher and Underwriter agents working collaboratively  
- **AI-Powered Analysis**: Uses Gemini or Ollama LLMs for intelligent decision making  
- **Interactive Sessions**: Human underwriters can interact continuously with the system  
- **Real-time Search**: DuckDuckGo integration for business information lookup  
- **Comprehensive Reporting**: Generate detailed loan assessment reports  
- **A2A Communication**: Agents communicate seamlessly through custom protocol  
- **MCP Tools**: Modular tools for data fetching, analysis, and search  

### 🏗️ System Architecture
```
┌─────────────────────┐     A2A Protocol      ┌─────────────────────┐
│                     │◄─────────────────────►│                     │
│  Underwriter Agent  │                       │  DataFetcher Agent  │
│  (Decision Making)  │                       │  (Data & Analysis)  │
│                     │                       │                     │
└──────────┬──────────┘                       └──────────┬──────────┘
           │                                              │
           │                                              │
      MCP Tools:                                     MCP Tools:
      - analyze_loan                                 - fetch_data
      - make_decision                                - search_business_info
      - human_interaction                            - financial_analysis

  ```
### 📋 Prerequisites
- Python 3.8 or higher  
- pip (Python package manager)  
- Git  

### 🚀 Installation

**Clone the repository**
git clone https://github.com/01kumarr/loan-underwriting-system.git

cd loan-underwriting-system

**Activate virtual environment**
- venv\Scripts\activate - > On Windows
- source venv/bin/activate - > On macOS/Linux
```
setup .env file**
### LLM Configuration
LLM_PROVIDER=gemini  # Options: gemini, ollama

### For Gemini (Google AI)
GOOGLE_API_KEY=your_gemini_api_key_here

### For Ollama (Local LLM) - Optional
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Product Directory:
```
loan-underwriting-system/
├── agents/
│   ├── __init__.py             # Agent package init
│   ├── datafetcher.py          # DataFetcher agent with A2A handler
│   ├── mcp_tools.py            # MCP tool definitions
│   └── underwriter.py          # Underwriter agent
├── data/
│   ├── gst.json                # GST data
│   ├── itr.json                # Income tax returns
│   └── bank_statement.json     # Bank statements
├── a2a_protocol.py             # Agent-to-Agent communication protocol
├── llm_provider.py             # LLM configuration (Gemini/Ollama)
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
└── README.md                   # This file

```
### 🔧 Configuration
Using Gemini (Recommended)

Get API key from Google AI Studio

Add to .env: GOOGLE_API_KEY=your_key_here

Using Ollama (Local LLM)

Install Ollama from ollama.ai

Pull a model: ollama pull llama2

Update .env: LLM_PROVIDER=ollama

🐛 Troubleshooting
Common Issues

"LLM Provider not found" error

Check your .env file formatting

Ensure no inline comments in environment variables

"Data file not found" error

Create the data directory

Add required JSON files (gst.json, itr.json, bank_statement.json)

"API key not found" error

Add your Gemini API key to .env

Or switch to Ollama for local LLM

Search not returning results

DuckDuckGo API might be slow, wait a moment

Try searching with different terms

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Built with FastMCP framework

Uses Google's Gemini AI for intelligent analysis

DuckDuckGo for privacy-focused search functionality

📞 Support
For issues, questions, or contributions, please open an issue on GitHub or contact the maintainers.

## Note: This is a demonstration system. For production use, additional security measures, data validation, and compliance checks should be implemented


