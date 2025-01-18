from llmlingua import PromptCompressor

from ollama import chat
from ollama import ChatResponse

def comprimir(prompt, instruction = "", question = ""):
  target_token = int(len(prompt.split(" ")) * 0.9)
  print(f"Target token: {target_token}")
  llm_lingua = PromptCompressor(device_map="cpu")

  compressed_prompt = llm_lingua.compress_prompt(
    prompt, 
    instruction=instruction, 
    question=question, 
    target_token=target_token
  )
  print("\n:::::MENSAJE COMPRIMIDO TOTAL:::::\n", compressed_prompt)
  print("\n:::::MENSAJE COMPRIMIDO SECTIONED:::::\n", compressed_prompt['compressed_prompt'])
  return compressed_prompt['compressed_prompt']