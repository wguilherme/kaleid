from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import time
import logging
from datetime import datetime, timezone
from typing import Dict
import json


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class MongoDBHandler:
    def __init__(self, config, max_retries=3, retry_delay=5):
        """
        Initialize MongoDB connection with retry mechanism
        
        Args:
            config: Configuration dictionary
            max_retries: Maximum number of connection attempts
            retry_delay: Delay between retries in seconds
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configurações de conexão
        self.uri = config.get('MONGODB_URI')
        self.db_name = config.get('MONGODB_DATABASE', 'kaleid')
        self.collection_name = config.get('MONGODB_COLLECTION', 'summaries')
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Tentativas de conexão
        for attempt in range(max_retries):
            try:
                # Adiciona timeouts e configurações de conexão
                self.mongo_client = MongoClient(
                    self.uri,
                    serverSelectionTimeoutMS=5000,  # 5 segundos para seleção do servidor
                    connectTimeoutMS=5000,          # 5 segundos para conexão
                    socketTimeoutMS=5000,           # 5 segundos para operações
                    maxPoolSize=50,                 # Máximo de conexões no pool
                    retryWrites=True                # Retry em operações de escrita
                )
                
                # Testa a conexão
                self.mongo_client.admin.command('ping')
                
                self.db = self.mongo_client[self.db_name]
                self.collection = self.db[self.collection_name]
                
                self.logger.info("Successfully connected to MongoDB")
                break
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                if attempt == max_retries - 1:  # Última tentativa
                    self.logger.error(f"Could not connect to MongoDB after {max_retries} attempts: {str(e)}")
                    raise
                else:
                    self.logger.warning(f"Failed to connect to MongoDB (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)

    def __del__(self):
        """Cleanup connection on object destruction"""
        if hasattr(self, 'mongo_client'):
            self.mongo_client.close()

    def check_connection(self) -> bool:
        """Verify if MongoDB connection is still alive"""
        try:
            self.mongo_client.admin.command('ping')
            return True
        except Exception as e:
            self.logger.error(f"MongoDB connection check failed: {str(e)}")
            return False

    def reconnect(self):
        """Reconnect to MongoDB if connection is lost"""
        try:
            self.mongo_client.close()
            self.__init__(self.config)
        except Exception as e:
            self.logger.error(f"Failed to reconnect to MongoDB: {str(e)}")
            raise

    def serialize_document(self, data: Dict) -> Dict:
        """
        Serialize document ensuring all fields are MongoDB-compatible
        
        Args:
            data: Dictionary to serialize
            
        Returns:
            Dict: Serialized dictionary
        """
        try:
            # Primeiro converte para JSON string usando o encoder personalizado
            json_str = json.dumps(data, cls=DateTimeEncoder)
            # Depois converte de volta para dict
            return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error serializing document: {str(e)}")
            raise

    def save_to_mongodb(self, data: Dict) -> bool:
        """
        Save data to MongoDB with retry mechanism
        
        Args:
            data: Dictionary containing the data to be saved
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not data:
            self.logger.error("Cannot save empty data to MongoDB")
            return False

        for attempt in range(self.max_retries):
            try:
                # Verifica conexão antes de salvar
                if not self.check_connection():
                    self.logger.warning("Connection lost, attempting to reconnect...")
                    self.reconnect()

                # Adiciona timestamp de criação se não existir
                if 'created_at' not in data:
                    data['created_at'] = datetime.now(timezone.utc)
                
                # Adiciona timestamp de atualização
                data['updated_at'] = datetime.now(timezone.utc)
                
                # Serializa o documento antes de salvar
                serialized_data = self.serialize_document(data)
                
                result = self.collection.insert_one(serialized_data)
                
                if result.inserted_id:
                    self.logger.info(f"Successfully saved document to MongoDB with ID: {result.inserted_id}")
                    return True
                else:
                    self.logger.error("Failed to save document to MongoDB: no inserted_id returned")
                    return False
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Failed to save to MongoDB (attempt {attempt + 1}/{self.max_retries}). "
                                      f"Retrying in {self.retry_delay} seconds... Error: {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Could not save to MongoDB after {self.max_retries} attempts: {str(e)}")
                    return False

        return False