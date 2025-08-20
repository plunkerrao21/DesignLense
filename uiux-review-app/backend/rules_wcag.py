from PIL import Image
import math
from typing import List, Dict, Tuple

def rgb_to_relative_luminance(r: int, g: int, b: int) -> float:
    """Convert RGB to relative luminance for contrast calculation"""
    def linearize(c):
        c = c / 255.0
        if c <= 0.03928:
            return c / 12.92
        else:
            return math.pow((c + 0.055) / 1.055, 2.4)
    
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)

def contrast_ratio(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """Calculate contrast ratio between two RGB colors"""
    l1 = rgb_to_relative_luminance(*color1)
    l2 = rgb_to_relative_luminance(*color2)
    
    # Ensure lighter color is numerator
    if l1 > l2:
        return (l1 + 0.05) / (l2 + 0.05)
    else:
        return (l2 + 0.05) / (l1 + 0.05)

def get_wcag_level(ratio: float, large_text: bool = False) -> str:
    """Determine WCAG compliance level"""
    if large_text:
        if ratio >= 4.5:
            return "AAA"
        elif ratio >= 3.0:
            return "AA"
        else:
            return "Fail"
    else:
        if ratio >= 7.0:
            return "AAA"
        elif ratio >= 4.5:
            return "AA"
        else:
            return "Fail"

def sample_image_colors(image_path: str) -> List[Dict]:
    """Sample colors from key points in the image for contrast analysis"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            
            # Sample points: center and four corners
            sample_points = [
                (width // 2, height // 2, "center"),
                (width // 4, height // 4, "top-left"),
                (3 * width // 4, height // 4, "top-right"),
                (width // 4, 3 * height // 4, "bottom-left"),
                (3 * width // 4, 3 * height // 4, "bottom-right")
            ]
            
            contrast_samples = []
            
            for x, y, location in sample_points:
                # Get color at sample point
                pixel_color = img.getpixel((x, y))
                
                # Sample surrounding area to find potential text/background pairs
                region_size = min(50, width // 10, height // 10)
                x_start = max(0, x - region_size // 2)
                y_start = max(0, y - region_size // 2)
                x_end = min(width, x + region_size // 2)
                y_end = min(height, y + region_size // 2)
                
                # Get colors in the region
                region_colors = []
                for rx in range(x_start, x_end, 5):  # Sample every 5 pixels
                    for ry in range(y_start, y_end, 5):
                        region_colors.append(img.getpixel((rx, ry)))
                
                # Find the most contrasting color pair in the region
                max_contrast = 0
                best_fg = pixel_color
                best_bg = pixel_color
                
                for i, color1 in enumerate(region_colors[::3]):  # Sample subset for performance
                    for color2 in region_colors[i+1::3]:
                        ratio = contrast_ratio(color1, color2)
                        if ratio > max_contrast:
                            max_contrast = ratio
                            best_fg = color1 if rgb_to_relative_luminance(*color1) < rgb_to_relative_luminance(*color2) else color2
                            best_bg = color2 if best_fg == color1 else color1
                
                # Only include if we found meaningful contrast
                if max_contrast > 1.5:
                    contrast_samples.append({
                        "location": location,
                        "fg": f"#{best_fg[0]:02x}{best_fg[1]:02x}{best_fg[2]:02x}",
                        "bg": f"#{best_bg[0]:02x}{best_bg[1]:02x}{best_bg[2]:02x}",
                        "ratio": round(max_contrast, 2),
                        "passes": get_wcag_level(max_contrast),
                        "passes_large": get_wcag_level(max_contrast, large_text=True)
                    })
            
            return contrast_samples
            
    except Exception as e:
        print(f"Error sampling image colors: {e}")
        return []

def analyze_contrast(image_path: str) -> Dict:
    """Perform WCAG contrast analysis on an image"""
    samples = sample_image_colors(image_path)
    
    # Calculate summary statistics
    total_samples = len(samples)
    aa_passes = len([s for s in samples if s["passes"] in ["AA", "AAA"]])
    aaa_passes = len([s for s in samples if s["passes"] == "AAA"])
    
    return {
        "contrast_samples": samples,
        "summary": {
            "total_samples": total_samples,
            "aa_compliance": f"{aa_passes}/{total_samples}" if total_samples > 0 else "0/0",
            "aaa_compliance": f"{aaa_passes}/{total_samples}" if total_samples > 0 else "0/0",
            "note": "Estimated from screenshot samples. Precise contrast requires design source colors."
        }
    }
