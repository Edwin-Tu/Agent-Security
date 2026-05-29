class LLMGatewayError(Exception):
    pass

class OllamaConnectionError(LLMGatewayError):
    pass

class OllamaModelNotFoundError(LLMGatewayError):
    pass

class OllamaTimeoutError(LLMGatewayError):
    pass

class OllamaGenerationError(LLMGatewayError):
    pass

class OllamaStreamError(LLMGatewayError):
    pass

class InvalidModelOptionsError(LLMGatewayError):
    pass
