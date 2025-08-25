from transformers import AutoTokenizer

class DeepseekTokenizer:
	TOKEN_LIMIT = 120000

	def __init__(self):
		self.tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")

	def get_token_count(self, prompt):
		encodings = self.tokenizer(prompt)
		return len(encodings)