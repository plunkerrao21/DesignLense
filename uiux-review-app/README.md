# UI/UX Screenshot Reviewer

A complete, AI-powered web application that analyzes UI screenshots and provides structured feedback mapped to established UI/UX laws and accessibility guidelines. Features Google Gemini Vision integration, WCAG contrast checking, and a modern web interface.

## Features

- **AI-Powered Analysis**: Uses Google Gemini Vision (with OpenRouter/Groq fallbacks)
- **UI/UX Law Mapping**: Structured feedback based on 15+ design principles
- **WCAG Contrast Checking**: Automated color contrast analysis
- **Modern Web Interface**: Responsive design with dark mode support
- **Drag & Drop Upload**: Intuitive file upload with preview
- **PDF Export**: Print-friendly reports for sharing

## Project Structure

```
uiux-review-app/
├── backend/
│   ├── app.py                # FastAPI server with AI integration
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment variables template
│   ├── laws_loader.py       # UI/UX laws loader utility
│   └── rules_wcag.py        # WCAG contrast analysis
├── frontend/
│   ├── index.html           # Main web interface
│   ├── style.css            # Responsive styling with themes
│   └── script.js            # Client-side functionality
├── shared/
│   └── laws.json            # Canonical UI/UX laws database
└── README.md
```

## Quick Start

### 1. Backend Setup

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your API key:
```bash
# Required: Get from https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here

# Optional fallbacks
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key
```

Install dependencies and run:
```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### 2. Frontend Usage

Open `frontend/index.html` in your browser or serve it locally:
```bash
# Optional: serve with Python
cd frontend
python -m http.server 5173
```

### 3. Using the Web Application

1. Upload a UI screenshot by dragging and dropping or clicking "browse files"
2. Add optional notes about your design
3. Click "Analyze Design" to get AI-powered feedback
4. Review the comprehensive analysis and download a PDF report if needed

## API Endpoints

### `POST /analyze`
Analyzes uploaded UI screenshots.

**Request:**
- `file`: Image file (PNG/JPG/WebP, max 8MB)
- `notes`: Optional context notes

**Response:**
```json
{
  "analysis": "Analysis summary",
  "strengths": ["List of design strengths"],
  "issues": ["List of identified issues"],
  "laws_feedback": {
    "Fitts's Law": "Specific feedback for this law",
    "Hick's Law": "Specific feedback for this law"
  },
  "suggestions": ["Prioritized improvement suggestions"],
  "step_by_step_improvements": ["Ordered action items"],
  "checks": {
    "contrast_samples": [
      {
        "location": "center",
        "fg": "#333333",
        "bg": "#ffffff", 
        "ratio": 12.63,
        "passes": "AAA"
      }
    ],
    "summary": {
      "total_samples": 5,
      "aa_compliance": "4/5",
      "aaa_compliance": "3/5"
    }
  },
  "model": {
    "provider": "gemini",
    "name": "gemini-1.5-flash-latest",
    "latency_ms": 1234
  }
}
```

### `GET /laws`
Returns the complete UI/UX laws database.

### `GET /health`
Health check endpoint.

## UI/UX Laws Covered

The application analyzes designs against these established principles:

- **Fitts's Law**: Target size and distance relationships
- **Hick's Law**: Decision complexity and choice overload
- **Miller's Law**: Cognitive load and information chunking
- **Jakob's Law**: User expectations and familiar patterns
- **Aesthetic–Usability Effect**: Visual appeal impact on usability
- **Doherty Threshold**: Response time expectations
- **Tesler's Law**: Complexity conservation
- **Serial Position Effect**: Information positioning
- **Von Restorff Effect**: Distinctive element memorability
- **Gestalt Principles**: Visual perception laws
  - Proximity, Similarity, Continuity, Closure
  - Figure-Ground, Prägnanz

## WCAG Contrast Analysis

The system performs automated contrast checking by:

1. Sampling colors from 5 key image locations
2. Computing relative luminance values
3. Calculating contrast ratios
4. Determining AA/AAA compliance levels

**Note**: Contrast analysis is estimated from screenshot pixels. For precise measurements, use design source files.

## Frontend Features

- **Drag & Drop Upload**: Intuitive file handling
- **Image Preview**: Visual confirmation before analysis
- **Dark/Light Themes**: User preference persistence
- **Responsive Design**: Works on desktop and mobile
- **Print Support**: Clean PDF generation via browser print
- **Error Handling**: Graceful degradation and user feedback

## Web Application Usage

1. **Upload**: Drag and drop your UI screenshot or click "browse files"
2. **Context**: Add optional notes about your design or specific concerns
3. **Analyze**: Click "Analyze Design" to get comprehensive AI feedback
4. **Review**: Examine strengths, issues, law-based feedback, and suggestions
5. **Export**: Download a PDF report for sharing or documentation

The application processes your image and provides detailed analysis within seconds.

## API Key Setup

### Google AI Studio (Primary)
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY`

### OpenRouter (Fallback)
1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Generate API key
3. Add to `.env` as `OPENROUTER_API_KEY`

### Groq (Fallback)
1. Sign up at [Groq](https://console.groq.com/)
2. Generate API key  
3. Add to `.env` as `GROQ_API_KEY`

## Security Notes

- API keys are stored server-side only
- Frontend never accesses sensitive credentials
- File uploads are validated and size-limited
- Temporary files are automatically cleaned up

## Limitations

- **Image Analysis**: AI estimates based on visual appearance
- **Contrast Checking**: Pixel sampling approximation
- **File Size**: 8MB maximum upload size
- **Supported Formats**: PNG, JPG, WebP only

## Troubleshooting

### Backend Won't Start
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Ensure port 8000 is available

### Analysis Fails
- Verify `GEMINI_API_KEY` in `.env` file
- Check API key validity and quota
- Ensure image file is valid and under 8MB

### File Upload Issues
- Ensure image is PNG, JPG, or WebP format
- Check file size is under 8MB
- Verify image is not corrupted

### Frontend Connection Issues
- Ensure backend is running on port 8000
- Check browser network tab for failed requests
- Verify CORS settings in `app.py`

## Development

### Adding New UI/UX Laws
Edit `shared/laws.json`:
```json
{
  "New Law Name": {
    "definition": "Brief explanation of the principle",
    "checklist": [
      "First actionable checkpoint",
      "Second actionable checkpoint", 
      "Third actionable checkpoint"
    ]
  }
}
```

### Customizing Analysis Prompt
Modify the prompt template in `backend/app.py` around line 85.

### Styling Changes
Edit `frontend/style.css` - uses CSS custom properties for easy theming.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the browser console for errors
3. Verify backend logs for API issues
4. Ensure all dependencies are correctly installed
