import logging
from langchain_core.messages import HumanMessage

class LLMModel:

    _instance = None
    _initialized = False
    _basic_model = None
    _advanced_model = None
    _validated = False

    def __new__(cls, *args, **kwargs):

        cls._instance = super(LLMModel, cls).__new__(cls)
        cls._instance._initialized = False
        cls._instance._basic_model = None
        cls._instance._advanced_model = None
        cls._instance._validated = False

        return cls._instance
    
    def __init__(self):
        pass

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = LLMModel()
        return cls._instance

    def initialize(self, basic_model=None, advanced_model=None, **kwargs):
        
        if not self._initialized:

            self._basic_model = basic_model
            self._advanced_model = advanced_model

            self._initialized = True
    
    @property
    def basic_model(self):
        if not self.test_models():
            logging.error("LLM models failed validation tests. Please check the logs for details.")
            return None
        return self._basic_model
    
    @property
    def advanced_model(self):
        if not self.test_models():
            logging.error("LLM models failed validation tests. Please check the logs for details.")
            return None
        return self._advanced_model
    
    def test_models(self):

        if self._validated:
            logging.info("LLM models have already been validated. Skipping tests.")
            return True
        
        status = True
        if self._basic_model:
            try:
                response = self._basic_model.invoke([HumanMessage(
                    content="Hello! This is a test. Please respond only: Basic Model is connected.")])
                logging.info(f"Basic model response: {response.content}")
                status = status and True
            except Exception as e:
                logging.error(f"Error invoking basic model: {e}")
                status = False
        
        if self._advanced_model:
            try:
                response = self._advanced_model.invoke([HumanMessage(
                    content="Hello! This is a test. Please respond only: Advanced Model is connected.")])
                logging.info(f"Advanced model response: {response.content}")
                status = status and True
            except Exception as e:
                logging.error(f"Error invoking advanced model: {e}")
                status = False

        self._validated = status
        return status
