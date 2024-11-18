# sources/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from openai import OpenAI
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

class DataSource(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.openai_client = OpenAI(api_key=config.get('openai_api_key'))

    def enrich(self, data: List[Dict]) -> List[Dict]:
        enriched_data = []
        
        for item in data:
            try:
                prompt = f"""
                Título: {item['title']}
                Descrição: {item['description']}
                
                Forneça um resumo conciso em 2-3 frases, destacando:
                - Principais fatos
                - Impacto ou relevância
                - Contexto importante
                """

                response = self.openai_client.chat.completions.create(
                    model=self.config.get('llm', {}).get('model', 'gpt-3.5-turbo'),
                    messages=[
                        {"role": "system", "content": "Você é um assistente especializado em análise e síntese de notícias."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config.get('llm', {}).get('temperature', 0.7),
                    max_tokens=self.config.get('llm', {}).get('max_tokens', 500)
                )

                summary = response.choices[0].message.content

                enriched_item = item.copy()
                enriched_item.update({
                    'individual_summary': summary,
                    'enriched_at': datetime.now().isoformat()
                })
                enriched_data.append(enriched_item)
                
            except Exception as e:
                self.logger.error(f"Error enriching item: {str(e)}")
                enriched_data.append(item)
                
        return enriched_data
    
    
    @staticmethod
    def clean_html(html_content: str) -> str:
        """Remove HTML tags and clean up text content."""
        if not html_content:
            return ''
        
        try:
            # Remove HTML tags
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            logger.error(f"Error cleaning HTML content: {str(e)}")
            return html_content
    
    @staticmethod
    def clean_and_truncate(html_content: str, max_length: int = 500) -> str:
        """Clean HTML and truncate to specified length."""
        clean_text = DataSource.clean_html(html_content)
        if len(clean_text) > max_length:
            return clean_text[:max_length] + '...'
        return clean_text


    def collect(self) -> List[Dict]:
        """Main method to fetch and process data"""
        raw_data = self.fetch()

        if not raw_data:
            self.logger.warning("No data fetched")
            return []
        
        self.logger.info(f"Processing data from {self.__class__.__name__}")
        processed_data = self.process(raw_data)
        self.logger.info(f"Data processed from {processed_data}")

        if not processed_data:
            self.logger.warning("No data processed")
            return []

                # Adicionar aqui o enrich
        enriched_data = self.enrich(processed_data)

        if not enriched_data:
            self.logger.warning("No data enriched")
            return []

        self.logger.info(f"Data enriched from {self.__class__.__name__}")
        self.logger.debug(f"Enriched data: {enriched_data}")
        
        return enriched_data

    def generate_master_summary(self, all_sources_data: List[Dict]) -> Dict:
        """Generate a master summary from all sources"""
        try:
            # Agrupa sumários por fonte
            summaries_by_source = {}
            for item in all_sources_data:
                source = item.get('source', 'unknown')
                if source not in summaries_by_source:
                    summaries_by_source[source] = []
                if 'individual_summary' in item:
                    summaries_by_source[source].append(item['individual_summary'])

            # Cria prompt para resumo final
            prompt = "Analisando todas as notícias coletadas:\n\n"
            
            for source, summaries in summaries_by_source.items():
                prompt += f"\nFonte: {source}\n"
                for summary in summaries:
                    prompt += f"- {summary}\n"

            prompt += """
            Por favor, gere:
            1. Um resumo geral dos principais acontecimentos
            2. Conexões ou padrões entre as notícias
            3. Tópicos mais relevantes
            4. Uma análise do cenário geral
            """

            master_summary = self._call_llm(prompt)

            return {
                'master_summary': master_summary,
                'source_count': len(summaries_by_source),
                'total_items': sum(len(s) for s in summaries_by_source.values()),
                'generated_at': datetime.now().isoformat(),
                'sources': list(summaries_by_source.keys())
            }

        except Exception as e:
            self.logger.error(f"Error generating master summary: {str(e)}")
            return {
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }

    def _call_llm(self, prompt: str) -> str:

        logger.info(f"Calling LLM API with prompt: {prompt}")
        
        """Helper method to call LLM API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.config.get('llm', {}).get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise e síntese de notícias."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('llm', {}).get('temperature', 0.7),
                max_tokens=self.config.get('llm', {}).get('max_tokens', 500)
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM API error: {str(e)}")
            return ""
