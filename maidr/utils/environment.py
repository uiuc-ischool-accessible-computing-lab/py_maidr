import json
import os


class Environment:
    @staticmethod
    def is_interactive_shell() -> bool:
        """Return True if the environment is an interactive shell."""
        try:
            from IPython.core.interactiveshell import InteractiveShell

            return (
                InteractiveShell.initialized()
                and InteractiveShell.instance() is not None
            )
        except ImportError:
            return False

    @staticmethod
    def initialize_llm_secrets() -> str:
        """Inject the LLM API keys into the MAIDR instance."""

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        # Default settings for the MAIDR instance
        settings = {
            "vol": "0.5",
            "autoPlayRate": "500",
            "brailleDisplayLength": "32",
            "colorSelected": "#03c809",
            "MIN_FREQUENCY": "200",
            "MAX_FREQUENCY": "1000",
            "keypressInterval": "2000",
            "ariaMode": "assertive",
            "openAIAuthKey": "",
            "geminiAuthKey": "",
            "skillLevel": "basic",
            "skillLevelOther": "",
            "LLMModel": "openai",
            "LLMPreferences": "",
            "LLMOpenAiMulti": False,
            "LLMGeminiMulti": False,
            "autoInitLLM": True,
        }

        if gemini_api_key is not None and openai_api_key is not None:
            settings["geminiAuthKey"] = gemini_api_key
            settings["openAIAuthKey"] = openai_api_key
            settings["LLMOpenAiMulti"] = True
            settings["LLMGeminiMulti"] = True
            settings["LLMModel"] = "multi"
        elif openai_api_key is not None:
            settings["LLMOpenAiMulti"] = True
            settings["openAIAuthKey"] = openai_api_key
        elif gemini_api_key is not None:
            settings["LLMGeminiMulti"] = True
            settings["geminiAuthKey"] = gemini_api_key

        settings_data = json.dumps(settings)

        keys_injection_script = f"""
            function addKeyValueLocalStorage(iframeId, key, value) {{
                const iframe = document.getElementById(iframeId);

                if (iframe && iframe.contentWindow) {{
                    try {{
                        iframe.contentWindow.localStorage.setItem(key, value);
                    }} catch (error) {{
                        console.error('Error accessing iframe localStorage:', error);
                    }}
                }} else {{
                    console.error('Iframe not found or inaccessible.');
                }}
            }}

            addKeyValueLocalStorage(
                'maidr-iframe', 'settings_data', JSON.stringify({settings_data})
            );
        """

        return keys_injection_script
