from itertools import islice

import pandas as pd
import requests
from bs4 import BeautifulSoup
from reverso_api.context import ReversoContextAPI
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data


class ReversoConnection(ExperimentalBaseConnection[ReversoContextAPI]):
    def _connect(self, **kwargs) -> ReversoContextAPI:
        self.source_lang = kwargs.get("source_lang", "en")
        self.target_lang = kwargs.get("target_lang", "fr")
        self.source_text = kwargs.get("source_text", "I am awesome")
        self.target_text = kwargs.get("target_text", "")

        return ReversoContextAPI(
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            source_text=self.source_text,
            target_text=self.target_text,
        )

    def instance(self) -> ReversoContextAPI:
        """Retrieve the underlying connection object"""
        return self._instance

    def set_source_lang(self, source_lang: str) -> None:
        """Set the source language (default: en)"""
        self._instance.source_lang = source_lang

    def set_target_lang(self, target_lang: str) -> None:
        """Set the target language (default: fr)"""
        self._instance.target_lang = target_lang

    def set_source_text(self, source_text: str) -> None:
        """Set the source text (default: I am awesome)"""
        self._instance.source_text = source_text

    def set_target_text(self, target_text: str) -> None:
        """Set the target text (optional, default: None)"""
        self._instance.target_text = target_text

    def get_usage_translations(self, ttl: int = 3600) -> pd.DataFrame:
        """Get multiple translations of the source text from a source language to a target language"""
        @cache_data(ttl=ttl)
        def _get_usage_translations() -> pd.DataFrame:
            instance = self.instance()
            translations = instance.get_translations()

            translations_dct = {}
            for i, translation in enumerate(translations):
                translations_dct[i] = {
                    "translation": translation.translation,
                    "frequency": translation.frequency,
                    "part_of_speech": translation.part_of_speech,
                }

            df_translations = pd.DataFrame.from_dict(translations_dct, orient="index")
            return df_translations

        return _get_usage_translations()

    def get_usage_examples(self, n_ex: int = 10, ttl: int = 3600) -> pd.DataFrame:
        """Get usage examples of how to use the source & target texts in a sentence"""
        @cache_data(ttl=ttl)
        def _get_usage_examples(n_ex) -> pd.DataFrame:
            instance = self.instance()
            examples = islice(instance.get_examples(), n_ex)

            examples_dct = {}
            for i, example in enumerate(examples):
                source_example, target_example = example
                examples_dct[i] = {
                    "source": source_example.text,
                    "target": target_example.text,
                }

            df_examples = pd.DataFrame.from_dict(examples_dct, orient="index")
            return df_examples

        return _get_usage_examples(n_ex)

    def get_supported_langs(self, ttl: int = 3600) -> pd.DataFrame:
        """Get all supported languages from source and target"""
        @cache_data(ttl=ttl)
        def _get_supported_langs() -> pd.DataFrame:
            supported_langs = {}

            response = requests.get(
                "https://context.reverso.net/translation/",
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Content-Type": "application/json; charset=UTF-8",
                },
            )

            soup = BeautifulSoup(response.content, features="lxml")

            src_selector = soup.find("div", id="src-selector")
            trg_selector = soup.find("div", id="trg-selector")

            for selector, attribute in (
                (src_selector, "source_lang"),
                (trg_selector, "target_lang"),
            ):
                dd_spans = selector.find(class_="drop-down").find_all("span")
                langs = [span.get("data-value") for span in dd_spans]
                langs = [
                    lang for lang in langs if isinstance(lang, str) and len(lang) == 2
                ]

                supported_langs[attribute] = tuple(langs)
            
            df_supported_langs = pd.DataFrame.from_dict(supported_langs)

            return df_supported_langs

        return _get_supported_langs()
