from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
import time
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import tempfile
from typing import Optional
from laws_loader import load_laws
from rules_wcag import analyze_contrast

# Load environment variables
load_dotenv()

app = FastAPI(title="UI/UX Review API", version="1.0.0")

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Constants
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

def get_api_keys():
    """Get available API keys"""
    return {
        "gemini": os.getenv("GEMINI_API_KEY"),
        "openrouter": os.getenv("OPENROUTER_API_KEY"),
        "groq": os.getenv("GROQ_API_KEY")
    }

def encode_image_base64(image_path: str) -> str:
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_gemini_vision(image_path: str, notes: str = "") -> dict:
    """Call Gemini Vision API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    # Load laws for context
    laws = load_laws()
    laws_text = json.dumps(laws, indent=2)
    
    # Prepare the prompt
    system_prompt = "You are a senior UI/UX reviewer. Produce precise, actionable, non-generic feedback mapped to established UI/UX laws and accessibility guidelines. When uncertain, state assumptions."
    
    user_prompt = f"""Analyze the uploaded UI screenshot for:
1) Layout, spacing, alignment, grid usage, visual hierarchy
2) Typography (scale, contrast, readability), color usage (semantics, states), shadows/elevation
3) Accessibility (WCAG contrast, touch targets, keyboard focus affordances shown in the visual)
4) Navigation clarity and cognitive load
5) Map issues to these laws: Fitts's Law, Hick's Law, Miller's Law, Jakob's Law, Aesthetic–Usability Effect, Doherty Threshold, Tesler's Law, Serial Position Effect, Von Restorff, Gestalt (Proximity, Similarity, Continuity, Closure, Figure–Ground, Prägnanz)
Available laws reference:
{laws_text}
Return STRICT JSON (no markdown) with keys:
- strengths: string[]
- issues: string[]
- laws_feedback: {{ [law: string]: string }}  // actionable mapping per law
- suggestions: string[]                      // prioritized, concrete steps
- step_by_step_improvements: string[]        // 5–10 ordered steps to fix
If you reference contrast, estimate visually from the screenshot, but phrase as "estimated"; the server will attach a separate WCAG check.
Optional user notes: {notes}"""

    # Encode image
    image_base64 = encode_image_base64(image_path)
    
    # Prepare request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": f"{system_prompt}\n\n{user_prompt}"},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_base64
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 4096
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        latency_ms = int((time.time() - start_time) * 1000)
        
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Parse JSON response
            try:
                # Clean up the response (remove markdown if present)
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                analysis_data = json.loads(content)
                
                return {
                    "analysis_data": analysis_data,
                    "model": {
                        "provider": "gemini",
                        "name": "gemini-1.5-flash-latest",
                        "latency_ms": latency_ms
                    }
                }
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail="No response from Gemini API")
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Gemini API request failed: {str(e)}")

def call_openrouter_fallback(image_path: str, notes: str = "") -> dict:
    """Call OpenRouter as fallback"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="No fallback API keys available")
    
    # Similar implementation for OpenRouter
    # This is a simplified version - you'd implement the full OpenRouter API call
    raise HTTPException(status_code=500, detail="OpenRouter fallback not implemented in this demo")

def call_groq_fallback(image_path: str, notes: str = "") -> dict:
    """Call Groq as fallback"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="No fallback API keys available")
    
    # Similar implementation for Groq
    # This is a simplified version - you'd implement the full Groq API call
    raise HTTPException(status_code=500, detail="Groq fallback not implemented in this demo")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"ok": True}

@app.get("/laws")
async def get_laws():
    """Get UI/UX laws reference"""
    laws = load_laws()
    return laws

@app.post("/analyze")
async def analyze_screenshot(
    file: UploadFile = File(...),
    notes: Optional[str] = Form("")
):
    """Analyze UI screenshot with AI and rule-based checks"""
    
    # Validate file
    if not file.content_type or file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_TYPES)}"
        )
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Save temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(contents)
        temp_file_path = temp_file.name
    
    try:
        # Validate image
        try:
            with Image.open(temp_file_path) as img:
                img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Try AI analysis with fallbacks
        analysis_result = None
        api_keys = get_api_keys()
        
        try:
            if api_keys["gemini"]:
                analysis_result = call_gemini_vision(temp_file_path, notes or "")
            elif api_keys["openrouter"]:
                analysis_result = call_openrouter_fallback(temp_file_path, notes or "")
            elif api_keys["groq"]:
                analysis_result = call_groq_fallback(temp_file_path, notes or "")
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="No AI API keys configured. Please set GEMINI_API_KEY, OPENROUTER_API_KEY, or GROQ_API_KEY"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
        
        # Perform WCAG contrast analysis
        contrast_analysis = analyze_contrast(temp_file_path)
        
        # Combine results
        response_data = {
            "analysis": "AI-powered UI/UX analysis completed successfully",
            "strengths": analysis_result["analysis_data"].get("strengths", []),
            "issues": analysis_result["analysis_data"].get("issues", []),
            "laws_feedback": analysis_result["analysis_data"].get("laws_feedback", {}),
            "suggestions": analysis_result["analysis_data"].get("suggestions", []),
            "step_by_step_improvements": analysis_result["analysis_data"].get("step_by_step_improvements", []),
            "checks": contrast_analysis,
            "model": analysis_result["model"]
        }
        
        return JSONResponse(content=response_data)
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

# Best option for Windows - run with python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)