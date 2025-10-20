"""
CV Processor Module
Handles CV parsing and tailoring based on job requirements
"""

from typing import Dict
from .ollama_client import OllamaClient


class CVProcessor:
    """Processes and tailors CV to match job requirements"""

    def __init__(self, model: str = "llama3", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.ollama_client = OllamaClient()

    def tailor_cv(self, cv_text: str, job_data: Dict) -> str:
        """
        Tailor CV to match job requirements

        Args:
            cv_text: Original CV text
            job_data: Dictionary containing job information

        Returns:
            Tailored CV text
        """
        job_description = job_data.get('description', '')
        job_title = job_data.get('title', 'the position')

        system_prompt = """You are an expert CV/resume writer and career coach. 
Your task is to tailor a CV to match a specific job posting.

IMPORTANT RULES:
1. ONLY edit and rephrase existing content - DO NOT add fake experience or skills
2. Emphasize relevant skills and experience that match the job requirements
3. Reorder sections to highlight most relevant qualifications first
4. Use keywords from the job description naturally throughout the CV
5. Keep the same factual information - only improve presentation and emphasis
6. Maintain professional formatting and clear section headers
7. Keep it concise - ideally 1-2 pages
8. DO NOT fabricate or exaggerate - only reframe existing content

Focus on making the candidate's REAL experience shine for this specific role."""

        user_prompt = f"""Please tailor this CV for the following job:

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description[:1500]}

ORIGINAL CV:
{cv_text}

Please provide a tailored version that:
- Highlights relevant experience and skills for this specific job
- Uses keywords from the job description
- Maintains all truthful information
- Improves overall presentation for ATS compatibility

Return ONLY the tailored CV text, no explanations."""

        tailored_cv = self.ollama_client.generate(
            model=self.model,
            prompt=user_prompt,
            temperature=self.temperature,
            system_prompt=system_prompt
        )

        return tailored_cv if tailored_cv else cv_text

    def extract_key_skills(self, cv_text: str) -> list:
        """Extract key skills from CV"""
        prompt = f"""Extract the key technical and soft skills from this CV.
Return them as a comma-separated list.

CV:
{cv_text[:1000]}

Skills:"""

        response = self.ollama_client.generate(
            model=self.model,
            prompt=prompt,
            temperature=0.3
        )

        if response:
            skills = [s.strip() for s in response.split(',')]
            return skills
        return []


if __name__ == "__main__":
    # Test CV processor
    processor = CVProcessor()

    sample_cv = """John Doe
    Data Scientist

    Experience:
    - 3 years in machine learning
    - Python, TensorFlow, scikit-learn
    - Developed predictive models"""

    sample_job = {
        'title': 'Senior Data Scientist',
        'description': 'Looking for a data scientist with Python and ML experience'
    }

    result = processor.tailor_cv(sample_cv, sample_job)
    print(result)
