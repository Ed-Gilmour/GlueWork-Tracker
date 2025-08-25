import transformers

class DeepseekTokenizer:
	TOKEN_LIMIT = 120000

	def __init__(self):
		chat_tokenizer_dir = "./glue_work_bot"
		self.tokenizer = transformers.AutoTokenizer.from_pretrained(
				chat_tokenizer_dir, trust_remote_code=True
		)

	def get_token_count(self, prompt):
		encodings = self.tokenizer(prompt)
		return len(encodings)