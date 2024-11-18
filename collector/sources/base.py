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
        
        self.logger.info(f"Processing data, {self.__class__.__name__}")
        processed_data = self.process(raw_data)
        self.logger.info(f"Data processed from, {self.__class__.__name__}")

        if not processed_data:
            self.logger.warning("No data processed")
            return []

        # Adicionar aqui o enrich
        enriched_data = self.enrich(processed_data)

        if not enriched_data:
            self.logger.warning("No data enriched")
            return []

        self.logger.info(f"Data enriched from {self.__class__.__name__}")
        # self.logger.debug(f"Enriched data: {enriched_data}")

        try:
            master_summary = self.generate_master_summary(enriched_data)
            enriched_data.insert(0, {
                'type': 'master_summary',
                'title': 'Master Summary',
                'description': master_summary['master_summary'],
                'source': 'all_sources',
                'pub_date': datetime.now().isoformat(),
                'source_count': master_summary['source_count'],
                'total_items': master_summary['total_items'],
                'sources': master_summary['sources']
            })
        except Exception as e:
            self.logger.error(f"Error adding master summary: {str(e)}")
        
        return master_summary

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
            prompt = """Analisando todas as notícias coletadas:

    """
            for source, summaries in summaries_by_source.items():
                prompt += f"Fonte: {source}\n"
                for summary in summaries:
                    prompt += f"- {summary}\n"
                prompt += "\n"

            prompt += """
                 Forneça uma síntese executiva e objetiva seguindo este formato:
                - Mantenha cada tópico conciso, direto e focado apenas no essencial.
                - Priorize informações acionáveis e de alto impacto.
                - Use linguagem clara e evite redundâncias.
                """

            response = self.openai_client.chat.completions.create(
                model=self.config.get('llm', {}).get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "Você é um analista especializado em sintetizar informações de múltiplas fontes e identificar padrões relevantes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('llm', {}).get('temperature', 0.7),
                max_tokens=self.config.get('llm', {}).get('max_tokens', 1000)
            )

            master_summary = response.choices[0].message.content

             # Limpa o texto removendo marcadores Markdown
            master_summary = (master_summary
                .replace('**', '')  # Remove negrito
                .replace('\\n', ' ')  # Substitui \n literal por espaço
                .replace('\n', ' ')   # Substitui quebras de linha reais por espaço
                .replace('  ', ' ')   # Remove espaços duplos
                .strip()              # Remove espaços extras no início e fim
            )

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