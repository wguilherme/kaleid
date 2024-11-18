# processors/gpt.py
from openai import OpenAI
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class GPTProcessor:
    def __init__(self, api_key: str, system_prompt: str):
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = system_prompt
    
    def process(self, data: Dict) -> Dict:
        if data['type'] != 'news':
            return data
            
        try:
            user_content = f"""Title: {data['title']}
            Content: {data['description']}

            Summarize this news article in 2-3 sentences. Then provide:
            1. Main topic (1-3 words)
            2. Key entities mentioned
            3. Sentiment (positive/neutral/negative)"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7
            )
            
            data['gpt_analysis'] = {
                'summary': response.choices[0].message.content,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"GPT processing error: {str(e)}")
            data['gpt_analysis'] = {
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
            
        return data