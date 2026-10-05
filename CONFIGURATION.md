# CONFIGURATION
All config via .env (pydantic-settings). See .env.example.

## Resource Tuning (12GB RAM / CPU only)
| Key | Default | Notes |
|-----|---------|-------|
| CHUNK_SIZE | 800 | tokens/chars per chunk |
| CHUNK_OVERLAP | 120 | overlap |
| RETRIAL_TOP_K | 5 | retrieved chunks |
| EMBEDDING_MODEL | nomic-embed-text | local lightweight |
| OLLAMA_DEFAULT_MODEL | qwen2.5:3b-instruct | 3B Q4 ~2GB RAM |
| MAX_UPLOAD_MB | 100 | |
| OCR_ENABLED | true | |

Low RAM: reduce CHUNK_SIZE, RETRIEVAL_TOP_K, context_length.
