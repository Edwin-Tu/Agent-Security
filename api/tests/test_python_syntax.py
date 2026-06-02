import py_compile
from pathlib import Path


def test_http_gateway_python_files_compile():
    files = [
        "api/server.py",
        "api/schemas.py",
        "api/routes_health.py",
        "api/routes_analyze.py",
        "api/routes_models.py",
        "api/routes_chat.py",
        "api/routes_openai_compatible.py",
        "api/routes_ollama_compatible.py",
        "entry/secretguard_pipeline.py",
        "entry/main.py",
        "entry/errors.py",
        "entry/guard_result.py",
        "entry/pipeline_context.py",
        "llm_gateway/base_provider.py",
        "llm_gateway/ollama_provider.py",
    ]
    for file in files:
        py_compile.compile(str(Path(file)), doraise=True)
