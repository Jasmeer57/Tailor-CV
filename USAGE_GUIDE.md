# 📚 CV Tailor - Complete Usage Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Detailed Walkthrough](#detailed-walkthrough)
3. [Best Practices](#best-practices)
4. [Troubleshooting](#troubleshooting)
5. [Advanced Features](#advanced-features)

---

## Getting Started

### What You Need
- ✅ Python 3.8+ installed
- ✅ Ollama installed and running
- ✅ At least one LLM model downloaded
- ✅ Your CV in PDF or DOCX format
- ✅ Job posting URL or description

### First Time Setup (5 minutes)

**Step 1: Install Ollama**
```bash
# Visit https://ollama.ai and download
# Then download a model:
ollama pull llama3
```

**Step 2: Setup Project**
```bash
# Run the setup script
# On Linux/macOS:
chmod +x setup.sh
./setup.sh

# On Windows:
setup.bat
```

**Step 3: Launch App**
```bash
streamlit run app.py
```

---

## Detailed Walkthrough

### Scenario: Applying for a Data Scientist Role

**1. Find the Job**
- Go to LinkedIn/Indeed/StepStone
- Find the job you want
- Copy the URL

**2. Load Job in App**
- Open CV Tailor in browser
- Paste URL in "Job Posting URL" field
- Click "Scrape Job Description"
- Wait 5-10 seconds
- Review scraped description

**3. Upload Your CV**
- Click "Upload your CV"
- Select your PDF/DOCX file
- Wait for processing
- Verify text extraction in preview

**4. Configure Settings (Optional)**
- Sidebar: Select your preferred model
- Adjust "AI Creativity" slider
  - Lower (0.3-0.5): Conservative, minimal changes
  - Medium (0.6-0.8): Balanced approach
  - Higher (0.8-1.0): More creative rephrasing

**5. Generate Materials**
- Check both boxes (Tailor CV + Cover Letter)
- Enter company name if not auto-detected
- Click "Generate Tailored Application"
- Wait 30-60 seconds (depends on model)

**6. Review and Download**
- Read the tailored CV
- Check for any AI errors
- Read the cover letter
- Personalize if needed
- Download both as DOCX
- Final edit in Word/Google Docs

---

## Best Practices

### For Best Results

**CV Preparation:**
✅ Use a clean, well-formatted original CV
✅ Include measurable achievements
✅ Keep it factual and accurate
✅ Update before each use

**Job Description:**
✅ Use the official job posting
✅ Include full description, not just snippet
✅ Check for complete requirements list

**Review Generated Content:**
✅ Always read the output carefully
✅ Fix any factual errors
✅ Personalize the cover letter opening
✅ Adjust tone if needed
✅ Add specific company research

**Application Strategy:**
✅ Generate unique versions for each job
✅ Don't use same CV for multiple roles
✅ Customize company references
✅ Update based on feedback

### Common Mistakes to Avoid

❌ **Don't**: Submit without reviewing
✅ **Do**: Always proofread AI output

❌ **Don't**: Use vague job descriptions
✅ **Do**: Use complete, official postings

❌ **Don't**: Rely 100% on AI
✅ **Do**: Add personal touches

❌ **Don't**: Apply to jobs you're unqualified for
✅ **Do**: Target realistic positions

---

## Troubleshooting

### App Won't Start

**Problem**: `streamlit: command not found`
**Solution**: 
```bash
pip install streamlit
# Or activate virtual environment:
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

**Problem**: "Ollama is not running"
**Solution**:
```bash
# Start Ollama
ollama serve

# In another terminal, verify:
curl http://localhost:11434
```

### Scraping Issues

**Problem**: "Failed to scrape job"
**Solutions**:
1. Try manual paste instead of URL
2. Check if site requires login
3. Copy description from site manually
4. Check internet connection

**Sites that need manual entry**:
- LinkedIn (requires login)
- Some company career pages
- Password-protected listings

### Generation Issues

**Problem**: Generation takes forever
**Solutions**:
1. Use smaller model (`mistral` vs `llama3:70b`)
2. Close other apps to free RAM
3. Check CPU usage
4. Try lower temperature

**Problem**: Output quality is poor
**Solutions**:
1. Use better model (llama3 > mistral)
2. Provide more complete CV
3. Use full job description
4. Adjust temperature (try 0.7-0.8)
5. Regenerate (AI varies each time)

**Problem**: Output is too different from original
**Solutions**:
1. Lower temperature (0.3-0.5)
2. Edit prompts in code to be more conservative
3. Manually merge AI suggestions with original

### File Issues

**Problem**: CV upload fails
**Solutions**:
1. Ensure file is PDF or DOCX
2. Try re-saving file in different format
3. Check file isn't password protected
4. Verify file isn't corrupted

**Problem**: Can't download output
**Solutions**:
1. Check browser download settings
2. Try different browser
3. Save from text area manually
4. Check disk space

---

## Advanced Features

### Custom Models

You can use any Ollama model:

```bash
# List available models
ollama list

# Pull new model
ollama pull mistral
ollama pull codellama
ollama pull gemma2

# Use in app via sidebar dropdown
```

**Recommended by role type**:
- **Tech roles**: codellama, deepseek-coder
- **General**: llama3, mistral
- **Creative**: llama3:70b (requires 32GB RAM)
- **Fast generation**: phi, gemma

### Batch Processing

To process multiple jobs:
1. Save job descriptions as text files
2. Use manual paste mode
3. Copy-paste each description
4. Generate for each
5. Save with descriptive names

### Prompt Customization

Edit AI behavior by modifying prompts in:

**File**: `processors/cv_processor.py`
**Line**: `system_prompt =`

Example modification for tech roles:
```python
system_prompt = """You are an expert technical resume writer.
Focus on quantifiable achievements, technical skills, and 
project impact. Use industry-standard terminology."""
```

### API Integration (Advanced)

You can integrate this into your own tools:

```python
from processors.cv_processor import CVProcessor
from processors.cover_letter_generator import CoverLetterGenerator

# Initialize
cv_proc = CVProcessor(model="llama3")
cl_gen = CoverLetterGenerator(model="llama3")

# Process
tailored_cv = cv_proc.tailor_cv(cv_text, job_data)
cover_letter = cl_gen.generate_cover_letter(cv_text, job_data)
```

---

## Performance Optimization

### Speed Tips
1. Use GPU if available (Ollama auto-detects)
2. Close browser tabs to free RAM
3. Use quantized models (4-bit, 8-bit)
4. Generate CV and CL separately
5. Reduce max tokens in ollama_client.py

### Quality Tips
1. Use larger models for final versions
2. Generate multiple versions, pick best
3. Combine AI suggestions manually
4. Keep temperature at 0.7
5. Provide detailed job descriptions

---

## Support & Community

**Getting Help**:
- Check this guide first
- Review README.md
- Search Ollama docs
- Check Streamlit docs

**Contributing**:
- Report bugs via issues
- Suggest features
- Submit improvements
- Share success stories

---

**💡 Pro Tip**: Generate 2-3 versions of each application using different models or temperature settings, then combine the best parts from each!

