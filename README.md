# 📄 CV Tailor - AI-Powered Resume & Cover Letter Generator

An industry-ready web application that uses **local Ollama LLMs** to automatically tailor your CV and generate personalized cover letters based on job postings from LinkedIn, Indeed, StepStone, and other job boards.

**✨ 100% Free | 🔒 Fully Local | 🚀 Production-Ready**

---

## 🎯 Features

### Core Functionality
- ✅ **Job Scraping**: Automatically scrape job descriptions from URLs (LinkedIn, Indeed, StepStone)
- ✅ **CV Tailoring**: AI-powered CV optimization matching job requirements
- ✅ **Cover Letter Generation**: Personalized, professional cover letters
- ✅ **ATS Optimization**: Keyword optimization for Applicant Tracking Systems
- ✅ **Multiple Formats**: Support for PDF and DOCX input/output
- ✅ **Local AI**: Uses Ollama - completely private and free

### Technical Features
- 🔒 **Privacy First**: All processing happens locally on your machine
- 🚀 **Production Ready**: Error handling, logging, and robust architecture
- 🎨 **Modern UI**: Clean Streamlit interface with real-time feedback
- 📦 **Easy Setup**: Simple installation with pip
- 🔧 **Modular Design**: Easy to extend and customize

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- [Ollama](https://ollama.ai) installed and running

### Installation

1. **Install Ollama**
   ```bash
   # Visit https://ollama.ai and download for your OS
   # Or use these commands:

   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh

   # Windows: Download installer from ollama.ai
   ```

2. **Pull an LLM model**
   ```bash
   ollama pull llama3
   # or
   ollama pull mistral
   # or
   ollama pull gemma2
   ```

3. **Start Ollama server**
   ```bash
   ollama serve
   ```

4. **Clone and setup the project**
   ```bash
   # Create project directory
   mkdir cv-tailor-app
   cd cv-tailor-app

   # Copy all project files here

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open browser**
   - The app will automatically open at `http://localhost:8501`

---

## 📖 How to Use

### Step 1: Load Job Description
**Option A - From URL:**
1. Paste job posting URL (LinkedIn, Indeed, StepStone, etc.)
2. Click "Scrape Job Description"
3. Job details will be extracted automatically

**Option B - Manual Entry:**
1. Select "Paste Text" option
2. Copy and paste the full job description
3. Click "Use This Description"

### Step 2: Upload Your CV
- Click "Upload your CV"
- Select your resume file (PDF or DOCX format)
- The system will extract and process the text

### Step 3: Generate
1. Select options:
   - ✅ Tailor CV
   - ✅ Generate Cover Letter
2. (Optional) Enter company name
3. Click "Generate Tailored Application"

### Step 4: Download
- Download your tailored CV as DOCX
- Download your personalized cover letter as DOCX
- Review and edit as needed before submitting

---

## 🏗️ Project Structure

```
cv-tailor-app/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── scrapers/
│   ├── __init__.py
│   └── job_scraper.py             # Job posting scraper
├── processors/
│   ├── __init__.py
│   ├── cv_processor.py            # CV tailoring logic
│   ├── cover_letter_generator.py  # Cover letter generation
│   └── ollama_client.py           # Ollama API client
└── utils/
    ├── __init__.py
    └── file_handler.py            # File I/O operations
```

---

## 🛠️ Configuration

### Supported Job Sites
- ✅ LinkedIn
- ✅ Indeed (all regions)
- ✅ StepStone (DE, AT, NL, BE)
- ✅ Generic scraper for other sites

### Supported Models
Any Ollama model works, but recommended:
- **llama3** (Best quality)
- **mistral** (Fast & efficient)
- **gemma2** (Good balance)
- **codellama** (For tech roles)

### Adjustable Parameters
- **AI Creativity (Temperature)**: 0.0 (conservative) to 1.0 (creative)
- Default: 0.7 (balanced)

---

## 🔧 Advanced Usage

### Custom Prompts
Edit prompt templates in:
- `processors/cv_processor.py` - CV tailoring prompts
- `processors/cover_letter_generator.py` - Cover letter prompts

### Add New Job Sites
Add scraper logic in `scrapers/job_scraper.py`:

```python
def _scrape_custom_site(self, url: str) -> Optional[Dict]:
    # Add your scraping logic
    return {
        'title': 'Job Title',
        'company': 'Company Name',
        'description': 'Full description'
    }
```

### Use Different LLMs
In the sidebar, select from available Ollama models, or pull new ones:

```bash
ollama pull <model-name>
```

---

## 🐛 Troubleshooting

### "Ollama is not running"
```bash
# Start Ollama server
ollama serve

# Check if running
curl http://localhost:11434
```

### "No models found"
```bash
# Pull a model
ollama pull llama3

# List installed models
ollama list
```

### Scraping Fails
- Try the "Paste Text" option instead of URL
- Some sites require authentication (LinkedIn)
- Check your internet connection

### Slow Generation
- Use a smaller model (e.g., `mistral:7b` instead of `llama3:70b`)
- Reduce temperature
- Ensure Ollama has sufficient RAM

---

## 📊 System Requirements

### Minimum
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 10 GB free
- **OS**: Windows 10+, macOS 11+, Linux

### Recommended
- **CPU**: 8+ cores
- **RAM**: 16 GB
- **GPU**: NVIDIA GPU (optional, speeds up generation)
- **Storage**: 20 GB free

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional job site scrapers
- Better prompt engineering
- UI/UX enhancements
- Multi-language support
- Export to more formats (LaTeX, HTML)

---

## 📜 License

This project is provided as-is for personal and commercial use.

---

## 🙏 Acknowledgments

Built with:
- [Ollama](https://ollama.ai) - Local LLM runtime
- [Streamlit](https://streamlit.io) - Web framework
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping
- [python-docx](https://python-docx.readthedocs.io/) - Document generation

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Ollama documentation: https://ollama.ai/docs
3. Open an issue on GitHub

---

## 🎉 Success Tips

1. **Keep CV concise**: 1-2 pages work best
2. **Use keywords**: AI extracts keywords from job descriptions
3. **Review output**: Always review and personalize before sending
4. **Multiple versions**: Generate multiple versions and pick the best
5. **Be honest**: AI tailors, but doesn't fabricate experience

---

**Made with ❤️ for job seekers everywhere**

*Stop spending hours customizing applications. Let AI do the heavy lifting while you focus on landing interviews!*
