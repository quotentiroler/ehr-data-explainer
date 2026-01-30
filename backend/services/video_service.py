"""
Video Generation Service - Generate educational medical videos using Wan 2.2.

Uses Hugging Face Spaces Gradio API:
- Wan-AI/Wan2.2-T2V-1.3B (Text-to-Video Space)
"""
import asyncio
import base64
import time
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import aiofiles

# Thread pool for running sync gradio_client calls
_executor = ThreadPoolExecutor(max_workers=2)


class VideoGenerationService:
    """
    Generates medical educational videos using Wan 2.2 model via HuggingFace Spaces.
    
    Uses the Gradio Client API to call Wan 2.2 Spaces.
    """
    
    def __init__(self, hf_token: str):
        self.hf_token = hf_token
        # Use the official Wan 2.2 5B Space
        self.space_id = "Wan-AI/Wan-2.2-5B"
        
        # Setup output directory
        self.output_dir = Path(__file__).parent.parent / "generated_videos"
        self.output_dir.mkdir(exist_ok=True)
    
    def _generate_sync(self, prompt: str, duration: float = 2.0) -> str:
        """Synchronous video generation using gradio_client."""
        from gradio_client import Client, handle_file
        
        # Connect to the Space
        client = Client(self.space_id)
        
        # Call the generate_video function with correct parameters
        # API: image, prompt, height, width, duration_seconds, sampling_steps, guide_scale, shift, seed
        # For text-to-video, we pass image as None/empty
        # ULTRA minimal settings to stay under ZeroGPU free tier quota!
        result = client.predict(
            image=None,  # None for text-to-video mode
            prompt=prompt,
            height=320,   # Very low resolution
            width=576,    # 16:9 aspect ratio
            duration_seconds=1.0,  # Minimum 1-second clip
            sampling_steps=10,  # Absolute minimum steps
            guide_scale=5.0,
            shift=5.0,
            seed=-1,  # Random seed
            api_name="/generate_video"
        )
        
        print(f"📹 Raw result: {result}")
        
        # Result is a dict with 'video' key containing the file path
        if isinstance(result, dict):
            if 'video' in result:
                return result['video']
            # Could also be just a path
            return str(result)
        return result  # Returns path to generated video
    
    async def generate_video(
        self,
        prompt: str,
        patient_id: str,
        duration: float = 2.0,
        timeout: float = 300.0
    ) -> dict:
        """
        Generate a video from a text prompt using Wan 2.2 Space.
        
        Args:
            prompt: Text description of the video to generate
            patient_id: Patient ID for filename
            duration: Video duration in seconds (0.3-5)
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with video_path, video_base64, and generation_time
        """
        if not self.hf_token:
            raise ValueError("Hugging Face token not configured")
        
        start_time = time.time()
        print(f"🎬 Generating video with Wan 2.2 for prompt: {prompt[:80]}...")
        
        # Run sync gradio client in thread pool
        loop = asyncio.get_event_loop()
        try:
            video_path_result = await asyncio.wait_for(
                loop.run_in_executor(_executor, self._generate_sync, prompt, duration),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Video generation timed out after {timeout}s")
        
        print(f"📁 Video generated at: {video_path_result}")
        
        # Read the generated video
        async with aiofiles.open(video_path_result, "rb") as f:
            video_bytes = await f.read()
        
        # Save to our output directory
        timestamp = int(time.time())
        video_filename = f"{patient_id}_{timestamp}.mp4"
        local_video_path = self.output_dir / video_filename
        
        async with aiofiles.open(local_video_path, "wb") as f:
            await f.write(video_bytes)
        
        generation_time = time.time() - start_time
        print(f"✅ Video generated in {generation_time:.1f}s: {video_filename}")
        
        return {
            "video_path": str(local_video_path),
            "video_filename": video_filename,
            "video_base64": base64.b64encode(video_bytes).decode(),
            "generation_time": generation_time,
            "prompt_used": prompt
        }
