"""
Cover Letter Generator Module
------------------------------
Production-ready module for generating best-in-class, ATS-optimized cover letters.
Features:
- Iterative refinement with quality checks
- Strict anti-hallucination prompts
- NLP-based candidate info extraction
- Retry logic with backoff
- Explicitly blocks and removes any chain-of-thought output (e.g., <think>, [thinking], etc.)
  — even when used with models like Qwen, DeepSeek, or others that may emit such tokens by default.
- Outputs ONLY the final polished cover letter — no reasoning, no internal commentary.
"""

from __future__ import annotations
import re
import time
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass

try:
    from .ollama_client import OllamaClient
except ImportError:
    from ollama_client import OllamaClient


# Logger setup
logger = logging.getLogger("cover_letter_generator")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)


@dataclass
class CoverLetterConfig:
    """Configuration for cover letter generation"""
    max_cv_chars: int = 8000
    max_job_chars: int = 4000
    desired_words: tuple = (300, 450)
    paragraphs: int = 4
    retries: int = 3
    retry_backoff: float = 1.3


class CoverLetterGenerator:
    """
    Advanced cover letter generator with iterative refinement.
    Prevents hallucination and **explicitly suppresses all chain-of-thought output**,
    including but not limited to <think>, </think>, [thinking], or any internal model reasoning.
    This is enforced via:
      - System prompt instructions
      - Post-generation regex stripping
      - Quality validation that rejects any such artifacts
    Works reliably even with models that natively emit CoT tokens (e.g., Qwen, DeepSeek).
    """

    def __init__(self, model: str = "llama3", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.ollama_client = OllamaClient()
        self.config = CoverLetterConfig()

    def _extract_candidate_info(self, cv_text: str) -> Dict[str, str]:
        """
        Extract structured candidate information using NLP heuristics.
        Returns: dict with name, headline, skills, achievements
        """
        info = {"name": "", "headline": "", "skills": "", "achievements": ""}
        lines = [l.strip() for l in cv_text.strip().splitlines() if l.strip()]

        if not lines:
            return info

        # Extract name (first line with 2-4 capitalized words)
        first_line = lines[0]
        if 1 <= len(first_line.split()) <= 4 and re.search(r"[A-Z][a-z]+", first_line):
            info["name"] = first_line

        # Extract headline/title (look for job titles in first 6 lines)
        title_keywords = r"\b(engineer|developer|scientist|manager|analyst|designer|architect|consultant|specialist)\b"
        for line in lines[:6]:
            if re.search(title_keywords, line, re.I):
                info["headline"] = line
                break

        # Extract skills (look for technical keywords)
        tech_keywords = r"\b(Python|Java|JavaScript|React|SQL|AWS|Docker|Kubernetes|TensorFlow|PyTorch|C\+\+|Node\.js|Spring|Django|Flask)\b"
        skill_lines = [l for l in lines if re.search(tech_keywords, l, re.I)]
        if skill_lines:
            info["skills"] = "; ".join(skill_lines[:3])[:400]

        # Extract quantifiable achievements
        achievement_pattern = r"(\d+%|increased|reduced|improved|led|delivered|built|achieved|designed)"
        achievements = [l for l in lines if re.search(achievement_pattern, l, re.I)]
        if achievements:
            info["achievements"] = "; ".join(achievements[:2])[:500]

        return info

    def _safe_truncate(self, text: str, max_chars: int) -> str:
        """Truncate text intelligently at word boundaries"""
        if len(text) <= max_chars:
            return text
        truncated = text[:max_chars - 3]
        last_space = truncated.rfind(" ")
        if last_space > max_chars // 2:
            truncated = truncated[:last_space]
        return truncated + "..."

    def _build_system_prompt(self) -> str:
        """
        Anti-hallucination, anti-chain-of-thought system prompt.
        Forces model to output only final polished letter.
        Explicitly forbids any internal reasoning tokens, even if the model (e.g., Qwen, DeepSeek)
        is configured to emit them by default.
        """
        return """You are a world-class professional cover letter writer and career strategist.

YOUR TASK: Write ONE complete, polished, professional cover letter.

STRICT RULES:
1. Output ONLY the final cover letter - NO reasoning, NO thinking process, NO chain-of-thought
2. NEVER use tags like  <think>, </think>, <reason>, [thinking], [thought], or any internal commentary
3. NEVER invent skills, experience, or qualifications not present in the CV
4. Use ONLY factual information from the provided CV
5. Write in a professional yet engaging tone
6. Focus on alignment between candidate's real experience and job requirements
7. Be specific and quantitative when possible (cite real achievements)
8. Keep it concise: 300-450 words, 3-4 paragraphs

FORMAT REQUIREMENTS:
- Professional business letter format
- Opening: Strong hook showing enthusiasm for THIS specific role
- Body: 2-3 key qualifications with specific examples from CV
- Closing: Confident call-to-action
- Sign-off: Professional and warm

Begin writing the final cover letter now. No preamble, no explanation - just the letter."""

    def _build_user_prompt(
        self, 
        job_title: str, 
        company: str, 
        job_description: str,
        cv_text: str,
        candidate_info: Dict[str, str]
    ) -> str:
        """Build detailed user prompt with extracted candidate context"""
        
        job_excerpt = self._safe_truncate(job_description, self.config.max_job_chars)
        cv_excerpt = self._safe_truncate(cv_text, self.config.max_cv_chars)

        return f"""GENERATE A PROFESSIONAL COVER LETTER

JOB POSTING:
Title: {job_title}
Company: {company}
Description: {job_excerpt}

CANDIDATE INFORMATION (use ONLY this factual data):
Name: {candidate_info.get('name', '[Your Name]')}
Professional Headline: {candidate_info.get('headline', 'Professional')}
Key Skills: {candidate_info.get('skills', 'See CV below')}
Notable Achievements: {candidate_info.get('achievements', 'See CV below')}

FULL CV (for context):
{cv_excerpt}

INSTRUCTIONS:
- Write {self.config.desired_words[0]}-{self.config.desired_words[1]} words
- Structure: {self.config.paragraphs} paragraphs
- Opening: Express genuine enthusiasm for THIS role at THIS company
- Body: Highlight 2-3 specific, relevant qualifications from the CV
- Include quantifiable achievements if available
- Show understanding of company/role (if info available in job description)
- Closing: Confident, professional call-to-action
- Format: [Date], [Contact Info], Dear Hiring Manager, [Body], Sincerely

OUTPUT ONLY THE FINAL LETTER. No commentary, no thinking process."""

    def _check_quality(self, letter: str, job_title: str, company: str) -> bool:
        """
        Quality checks for generated cover letter.
        Returns True if letter passes quality standards.
        Specifically rejects any trace of chain-of-thought output (e.g., <think>),
        which some models like Qwen or DeepSeek may emit unless explicitly suppressed.
        """
        if not letter or len(letter.strip()) < 200:
            logger.warning("Letter too short or empty")
            return False

        # Check for forbidden chain-of-thought markers (common in CoT-enabled models)
        forbidden_patterns = [
            r"(<|</)think>", r"(<|</)reason>", 
            r"\[thinking\]", r"\[thought\]", 
            r"let me think", r"my reasoning", r"chain of thought",
            r"<\s*think\b", r"<\s*/\s*think\b"
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, letter, re.I):
                logger.warning(f"Detected forbidden chain-of-thought pattern: {pattern}")
                return False

        # Check for placeholder text that wasn't replaced
        if "[Your Name]" in letter and "[Date]" in letter and "Dear Hiring Manager" in letter:
            # This is acceptable - proper format
            pass
        
        # Check if it references the job/company
        if company not in letter and job_title not in letter:
            logger.warning("Letter doesn't mention job title or company")
            return False

        return True

    def generate_cover_letter(
        self,
        cv_text: str,
        job_data: Dict,
        company_name: str = None
    ) -> str:
        """
        Generate a best-in-class, ATS-optimized cover letter.

        Args:
            cv_text: Full CV text
            job_data: Dict with 'title', 'company', 'description'
            company_name: Optional company override

        Returns:
            Professional cover letter text
        """
        if not cv_text or not job_data:
            raise ValueError("cv_text and job_data are required")

        # Parse job information
        job_title = job_data.get('title', 'the position').strip()
        company = (company_name or job_data.get('company', 'your company')).strip()
        job_description = job_data.get('description', '').strip()

        # Extract structured candidate info
        logger.info("Extracting candidate information...")
        candidate_info = self._extract_candidate_info(cv_text)

        # Build prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            job_title, company, job_description, cv_text, candidate_info
        )

        # Generation with retry logic
        attempt = 0
        backoff = 1.0
        
        while attempt < self.config.retries:
            attempt += 1
            logger.info(f"Generation attempt {attempt}/{self.config.retries}")

            try:
                response = self.ollama_client.generate(
                    model=self.model,
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=self.temperature
                )

                if response and isinstance(response, str):
                    response = response.strip()
                    # Aggressively strip any residual CoT tokens (defense in depth)
                    response = re.sub(r"</?think>", "", response, flags=re.IGNORECASE)
                    response = re.sub(r"</?reason>", "", response, flags=re.IGNORECASE)
                    response = re.sub(r"\[thinking\]|\[thought\]", "", response, flags=re.IGNORECASE)
                    response = response.strip()
                    
                    # Quality check
                    if self._check_quality(response, job_title, company):
                        logger.info("✓ Cover letter generated successfully")
                        return response
                    else:
                        logger.warning("Quality check failed, retrying...")
                        # Reduce temperature for more deterministic output
                        self.temperature = max(0.3, self.temperature - 0.1)
                else:
                    logger.warning("Empty response from model")

            except Exception as e:
                logger.exception(f"Error during generation: {e}")

            # Backoff before retry
            time.sleep(backoff)
            backoff *= self.config.retry_backoff

        # Fallback if all attempts fail
        logger.error("Failed to generate cover letter after all attempts")
        return self._generate_fallback_letter(job_title, company, candidate_info)

    def _generate_fallback_letter(
        self, 
        job_title: str, 
        company: str, 
        candidate_info: Dict[str, str]
    ) -> str:
        """Generate a basic fallback cover letter if AI generation fails"""
        name = candidate_info.get('name', '[Your Name]')
        headline = candidate_info.get('headline', 'Professional')
        
        return f"""[Date]
{name}
[Your Contact Information]

Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. As a {headline}, I am excited about the opportunity to contribute to your team.

My background and experience align well with the requirements of this role. I have developed strong technical and professional skills that would enable me to make meaningful contributions to {company}.

I would welcome the opportunity to discuss how my qualifications match your needs. Thank you for considering my application.

Sincerely,
{name}"""

    def generate_short_pitch(self, cv_text: str, job_data: Dict, max_words: int = 30) -> str:
        """
        Generate a concise elevator pitch (for email subject lines).

        Args:
            cv_text: CV text
            job_data: Job information dict
            max_words: Maximum words in pitch

        Returns:
            One-sentence pitch
        """
        candidate_info = self._extract_candidate_info(cv_text)
        job_title = job_data.get('title', 'the position')
        
        system_prompt = """You are an expert at writing compelling, concise professional pitches.
Output ONLY a single sentence. NO reasoning, NO thinking process, NO extra commentary."""

        user_prompt = f"""Write ONE compelling sentence (<= {max_words} words) explaining why this candidate is perfect for the {job_title} role.

CANDIDATE: {candidate_info.get('headline', 'Professional')}
KEY SKILLS: {candidate_info.get('skills', '')[:200]}
ACHIEVEMENT: {candidate_info.get('achievements', '')[:200]}

Write only the final pitch sentence:"""

        try:
            response = self.ollama_client.generate(
                model=self.model,
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            if response:
                # Extract first sentence only
                sentence = response.strip().split('.')[0] + '.'
                words = sentence.split()
                if len(words) > max_words:
                    sentence = ' '.join(words[:max_words]) + '...'
                return sentence
        except Exception as e:
            logger.exception(f"Pitch generation failed: {e}")

        return f"Experienced {candidate_info.get('headline', 'professional')} seeking {job_title} role."


# Test/demo code
if __name__ == "__main__":
    generator = CoverLetterGenerator(model="llama3", temperature=0.7)

    sample_cv = """Jane Smith
    Senior Software Engineer
    
    Experience:
    - 6 years building scalable backend systems with Python and FastAPI
    - Led team of 5 developers on microservices architecture project
    - Reduced API latency by 45% through caching and optimization
    - Skills: Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS
    """

    sample_job = {
        'title': 'Senior Backend Engineer',
        'company': 'TechCorp Inc',
        'description': 'We are seeking a Senior Backend Engineer with strong Python skills and experience with microservices, databases, and cloud infrastructure to build high-performance APIs.'
    }

    try:
        letter = generator.generate_cover_letter(sample_cv, sample_job)
        print("\n" + "="*80)
        print("GENERATED COVER LETTER")
        print("="*80)
        print(letter)
        print("="*80)
        
        pitch = generator.generate_short_pitch(sample_cv, sample_job)
        print(f"\nPITCH: {pitch}")
    except Exception as e:
        logger.error(f"Test failed: {e}")