"""
Video Generation Service - Generate educational medical videos using Wan 2.2.

Uses Hugging Face Inference API with Wan 2.2 models:
- Wan-AI/Wan2.2-T2V-A14B-Diffusers (Text-to-Video)
- Wan-AI/Wan2.2-I2V-A14B-Diffusers (Image-to-Video)
"""
import asyncio
import base64
import time
from pathlib import Path
from typing import Optional

import httpx
import aiofiles


# Pre-generated video templates for common conditions (fallback)
VIDEO_TEMPLATES = {
    "atrial_fibrillation": {
        "video_url": "/static/videos/heart_afib.mp4",
        "description": "Heart with irregular electrical signals",
        "conditions": ["I48", "atrial fibrillation", "afib", "I48.0", "I48.1", "I48.2"]
    },
    "type2_diabetes": {
        "video_url": "/static/videos/pancreas_insulin.mp4",
        "description": "Pancreas and insulin regulation",
        "conditions": ["E11", "type 2 diabetes", "t2dm", "E11.9", "E11.65"]
    },
    "hypertension": {
        "video_url": "/static/videos/blood_pressure.mp4",
        "description": "Blood vessels and pressure",
        "conditions": ["I10", "hypertension", "high blood pressure"]
    },
    "heart_failure": {
        "video_url": "/static/videos/heart_pumping.mp4",
        "description": "Heart pumping function",
        "conditions": ["I50", "heart failure", "chf", "I50.9"]
    },
    "copd": {
        "video_url": "/static/videos/lungs_breathing.mp4",
        "description": "Lungs and breathing",
        "conditions": ["J44", "copd", "chronic obstructive"]
    },
    "asthma": {
        "video_url": "/static/videos/airways.mp4",
        "description": "Airways and breathing",
        "conditions": ["J45", "asthma"]
    },
    "general": {
        "video_url": "/static/videos/body_health.mp4",
        "description": "General body health",
        "conditions": []
    }
}


class VideoGenerationService:
    """
    Generates medical educational videos using Wan 2.2 model.
    
    For hackathon demo:
    - Uses Hugging Face Inference API
    - Falls back to pre-generated templates if generation fails/slow
    
    For production:
    - Consider fal.ai or Replicate for faster generation
    - Or run locally with diffusers (requires GPU)
    """
    
    def __init__(self, hf_token: str):
        self.hf_token = hf_token
        self.api_url = "https://api-inference.huggingface.co/models/Wan-AI/Wan2.2-T2V-A14B-Diffusers"
        self.headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
        
        # Setup output directory
        self.output_dir = Path(__file__).parent.parent.parent / "generated_videos"
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_video(
        self,
        prompt: str,
        patient_id: str,
        num_frames: int = 49,  # ~2 seconds at 24fps
        height: int = 480,
        width: int = 832,
        timeout: float = 300.0
    ) -> dict:
        """
        Generate a video from a text prompt using Wan 2.2.
        
        Args:
            prompt: Text description of the video to generate
            patient_id: Patient ID for filename
            num_frames: Number of frames (49 ≈ 2 seconds at 24fps)
            height: Video height in pixels
            width: Video width in pixels
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with video_path, video_base64, and generation_time
        """
        if not self.hf_token:
            raise ValueError("Hugging Face token not configured")
        
        start_time = time.time()
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_frames": num_frames,
                "height": height,
                "width": width,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
            }
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Retry logic for model warm-up
            for attempt in range(3):
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 503:
                    # Model loading, wait and retry
                    print(f"⏳ Model loading, attempt {attempt + 1}/3...")
                    await asyncio.sleep(20)
                    continue
                
                if response.status_code == 200:
                    break
                    
                response.raise_for_status()
            
            video_bytes = response.content
        
        # Save video to disk
        timestamp = int(time.time())
        video_filename = f"{patient_id}_{timestamp}.mp4"
        video_path = self.output_dir / video_filename
        
        async with aiofiles.open(video_path, "wb") as f:
            await f.write(video_bytes)
        
        generation_time = time.time() - start_time
        
        return {
            "video_path": str(video_path),
            "video_filename": video_filename,
            "video_base64": base64.b64encode(video_bytes).decode(),
            "generation_time": generation_time,
            "prompt_used": prompt
        }
    
    def get_template_for_condition(self, condition_code: str) -> Optional[dict]:
        """
        Find best matching pre-generated video template for a condition.
        
        Args:
            condition_code: ICD-10 or SNOMED code
            
        Returns:
            Template dict with video_url, or None if no match
        """
        condition_lower = condition_code.lower()
        
        # Check each template for matching conditions
        for template_key, template in VIDEO_TEMPLATES.items():
            for cond in template["conditions"]:
                if cond.lower() in condition_lower or condition_lower.startswith(cond.lower()):
                    return template
        
        # Category-based fallbacks
        if condition_code.startswith("I"):
            # Cardiovascular
            if condition_code.startswith("I48"):
                return VIDEO_TEMPLATES.get("atrial_fibrillation")
            elif condition_code.startswith("I50"):
                return VIDEO_TEMPLATES.get("heart_failure")
            elif condition_code.startswith("I10"):
                return VIDEO_TEMPLATES.get("hypertension")
        
        if condition_code.startswith("E11"):
            return VIDEO_TEMPLATES.get("type2_diabetes")
        
        if condition_code.startswith("J44"):
            return VIDEO_TEMPLATES.get("copd")
        
        if condition_code.startswith("J45"):
            return VIDEO_TEMPLATES.get("asthma")
        
        # Default fallback
        return VIDEO_TEMPLATES.get("general")
    
    async def generate_with_reference_image(
        self,
        prompt: str,
        reference_image_path: Path,
        patient_id: str
    ) -> dict:
        """
        Generate video using image-to-video model for more control.
        
        Useful when we have medical diagram reference images to animate.
        """
        i2v_url = "https://api-inference.huggingface.co/models/Wan-AI/Wan2.2-I2V-A14B-Diffusers"
        
        async with aiofiles.open(reference_image_path, "rb") as f:
            image_bytes = await f.read()
        
        payload = {
            "inputs": {
                "prompt": prompt,
                "image": base64.b64encode(image_bytes).decode()
            },
            "parameters": {
                "num_frames": 49,
                "num_inference_steps": 30,
            }
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                i2v_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            video_bytes = response.content
        
        timestamp = int(time.time())
        video_filename = f"{patient_id}_i2v_{timestamp}.mp4"
        video_path = self.output_dir / video_filename
        
        async with aiofiles.open(video_path, "wb") as f:
            await f.write(video_bytes)
        
        return {
            "video_path": str(video_path),
            "video_filename": video_filename,
            "video_base64": base64.b64encode(video_bytes).decode()
        }
