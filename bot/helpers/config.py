import dotenv

# Load environment variables if they are not
# loaded by Docker or Docker is not used
def load_config():
	dotenv.load_dotenv(
		dotenv_path = "config.env",
		verbose = True
	)
