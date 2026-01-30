"""
Explanation Service - Generate patient-friendly health explanations using Claude.

Uses Anthropic's Claude API with optional Healthcare connectors for:
- ICD-10 code lookup
- PubMed evidence-based information
- FHIR resource handling
"""
import json
import anthropic
from .patient_service import PatientHealthSummary


class ExplanationService:
    """
    Generates patient-friendly health explanations using Claude.
    
    With Claude for Healthcare (Enterprise/Teams), you get:
    - Native FHIR parsing and generation
    - ICD-10 code lookup for accurate condition mapping
    - PubMed integration for evidence-based explanations
    - CMS coverage database for treatment context
    """
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    async def generate_health_explanation(
        self,
        summary: PatientHealthSummary,
        reading_level: str = "6th grade"
    ) -> dict:
        """
        Generate a patient-friendly explanation of their health situation.
        
        Args:
            summary: Patient health data from Neo4j
            reading_level: Target reading level for explanation
            
        Returns:
            Dictionary with structured explanation sections
        """
        prompt = f"""You are a caring health educator explaining a patient's health situation 
in simple, reassuring terms. Use analogies and everyday language.

Patient: {summary.patient_name}

Their health conditions:
{self._format_conditions(summary.conditions)}

Their medications:
{self._format_medications(summary.medications)}

Body systems affected:
{self._format_body_systems(summary.body_systems_affected)}

How conditions relate to each other:
{self._format_relationships(summary.condition_relationships)}

Please create a warm, educational explanation at a {reading_level} reading level that:
1. Explains what's happening in their body (use simple anatomical terms)
2. Why each medication helps
3. How their conditions connect to each other
4. Reassuring tone - focus on what IS working and how treatment helps

IMPORTANT: Include appropriate medical context but keep language accessible.
Always remind the patient to discuss questions with their healthcare provider.

Format the response as valid JSON:
{{
    "greeting": "A warm opening addressing the patient by name",
    "body_explanation": "What's happening inside their body (2-3 paragraphs)",
    "medication_explanation": "How their medications help (explain each one simply)",
    "connections": "How their conditions relate to each other",
    "encouragement": "Positive, supportive closing message",
    "key_takeaways": ["3-4 simple bullet points to remember"]
}}

Return ONLY the JSON, no other text."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON from response
        try:
            # Try to extract JSON if there's extra text
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Fallback structure if JSON parsing fails
            return {
                "greeting": f"Hello {summary.patient_name},",
                "body_explanation": response_text,
                "medication_explanation": "Please see your healthcare provider for medication details.",
                "connections": "Your conditions may be related. Ask your doctor for more information.",
                "encouragement": "You're taking important steps by learning about your health!",
                "key_takeaways": [
                    "Understanding your health is the first step",
                    "Your medications are helping your body",
                    "Always ask your healthcare team questions"
                ]
            }
    
    async def generate_video_prompt(
        self,
        summary: PatientHealthSummary,
        explanation: dict
    ) -> str:
        """
        Generate a detailed prompt for Wan 2.2 video generation.
        
        Creates a visual description for an educational medical animation
        that illustrates the patient's health situation.
        """
        # Determine primary body system for visualization
        primary_system = "body"
        if summary.body_systems_affected:
            primary_system = summary.body_systems_affected[0].get("system", "body").lower()
        
        conditions_list = [c.get("display", "") for c in summary.conditions[:3]]
        
        prompt = f"""Create a prompt for an AI video generator to make a calming medical educational animation.

Patient's main conditions: {', '.join(conditions_list)}
Primary body system: {primary_system}
Explanation context: {explanation.get('body_explanation', '')[:500]}

Write a detailed video generation prompt (under 200 words) that describes:
1. Visual style: Soft, medical illustration aesthetic with calming colors (blues, greens, soft whites)
2. Anatomical focus: The {primary_system} and related systems
3. Animation sequence: Show how the condition affects the body, then how treatment helps
4. Mood: Reassuring, educational, hopeful

DO NOT include text overlays or narration - just visual description.
Focus on ONE key concept to illustrate clearly.

Example format:
"Soft medical animation showing [specific anatomy]. Gentle [color] palette. The animation reveals [what happens], then shows [how treatment helps]. Calming, reassuring visual style suitable for patient education."

Write ONLY the video prompt, nothing else."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
    
    def _format_conditions(self, conditions: list[dict]) -> str:
        """Format conditions list for prompt."""
        if not conditions:
            return "No conditions recorded"
        return "\n".join([
            f"- {c.get('display', 'Unknown')} (code: {c.get('code', 'N/A')})"
            for c in conditions
        ])
    
    def _format_medications(self, medications: list[dict]) -> str:
        """Format medications list for prompt."""
        if not medications:
            return "No medications recorded"
        return "\n".join([
            f"- {m.get('display', 'Unknown')} (treats: {m.get('treats', 'condition')})"
            for m in medications
        ])
    
    def _format_body_systems(self, systems: list[dict]) -> str:
        """Format body systems list for prompt."""
        if not systems:
            return "No specific body systems identified"
        return "\n".join([
            f"- {s.get('system', 'Unknown')}: {s.get('description', '')}"
            for s in systems
        ])
    
    def _format_relationships(self, relationships: list[dict]) -> str:
        """Format condition relationships for prompt."""
        if not relationships:
            return "No known direct relationships between conditions"
        return "\n".join([
            f"- {r.get('condition', 'Condition')} → {r.get('related_to', 'Related condition')}"
            for r in relationships
            if r.get('related_to')
        ])
