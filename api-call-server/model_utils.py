from langchain_openai.chat_models.base import BaseChatOpenAI, ChatOpenAI

DEFAULT_MODEL = 'gpt-4o-mini-2024-07-18'
ADVANCED_MODEL = 'gpt-4o-2024-05-13'


def get_llm_model(
    model_name: str,
    temperature: float = 0.0,
    max_tokens: int = None,
    timeout: int = 115,
    max_retries: int = 27,
) -> BaseChatOpenAI:
  return ChatOpenAI(
      model_name=model_name,
      request_timeout=timeout,
      max_tokens=max_tokens,
      temperature=temperature,
      max_retries=max_retries
  )