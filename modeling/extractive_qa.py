import os
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from tqdm import tqdm
from psutil import cpu_count
from transformers import AutoTokenizer
from transformers import AutoModelForQuestionAnswering
from transformers.convert_graph_to_onnx import convert
from onnxruntime import GraphOptimizationLevel, InferenceSession, SessionOptions

from scraper.twitter import Twitter

os.environ["OMP_NUM_THREADS"] = f"{cpu_count()}"
os.environ["OMP_WAIT_POLICY"] = "ACTIVE"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class ExtractiveQA:

    INPUT_IDS = "input_ids"
    ANSWER = "answer"
    TAG_CLS = "[CLS]"
    QUESTIONS = "questions"
    TEXT = "text"
    GRAPH_PATH = "onnx/model.onnx"
    QUANT_PATH = "onnx/model.quant.onnx"

    def __init__(self, model_path: str):
        """_summary_
        :param model_path: _description_
        :type model_path: str
        """
        if os.path.isfile(ExtractiveQA.GRAPH_PATH):
            os.remove(ExtractiveQA.GRAPH_PATH)
        self._model_path = model_path
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_path)
        self._model = AutoModelForQuestionAnswering.from_pretrained(self._model_path)
        self._onnx_path = Path(ExtractiveQA.GRAPH_PATH)
        convert(
            framework="pt",
            model=self._model_path,
            tokenizer=self._tokenizer,
            output=self._onnx_path,
            opset=12,
            pipeline_name="question-answering",
        )
        self._model_onnx = self._create_model_for_provider()

    def answer_from_profile(self, profile: pd, question: str, keyword: str) -> pd:
        """_summary_
        :param profile: _description_
        :type profile: pd
        :param question: _description_
        :type question: str
        :param keyword: _description_
        :type keyword: str
        :return: _description_
        :rtype: pd
        """
        profile_filt = profile[profile[Twitter.TWEET_EN].str.contains(keyword)]
        tqdm.pandas()
        profile_filt[ExtractiveQA.ANSWER] = profile_filt[
            Twitter.TWEET_EN
        ].progress_apply(lambda x: self.answer(question, x))
        profile_filt = self._clean(profile_filt)
        return profile_filt

    def answer_from_profile_onnx(self, profile: pd, question: str, keyword: str) -> pd:
        """_summary_
        :param profile: _description_
        :type profile: pd
        :param question: _description_
        :type question: str
        :param keyword: _description_
        :type keyword: str
        :return: _description_
        :rtype: pd
        """
        profile_filt = profile[profile[Twitter.TWEET_EN].str.contains(keyword)]
        tqdm.pandas()
        profile_filt[ExtractiveQA.ANSWER] = profile_filt[
            Twitter.TWEET_EN
        ].progress_apply(lambda x: self.answer_onnx(question, x))
        profile_filt = self._clean(profile_filt)
        return profile_filt

    def answer(self, question: str, context: str) -> str:
        """_summary_
        :param question: _description_
        :type question: str
        :param context: _description_
        :type context: str
        :return: _description_
        :rtype: str
        """
        inputs = self._tokenizer(question, context, return_tensors="pt")
        with torch.no_grad():
            output = self._model(**inputs)
        start_logits = output.start_logits
        end_logits = output.end_logits
        start_idx = torch.argmax(start_logits)
        end_idx = torch.argmax(end_logits) + 1
        answer_span = inputs[ExtractiveQA.INPUT_IDS][0][start_idx:end_idx]
        return self._tokenizer.decode(answer_span)

    def answer_onnx(self, question: str, context: str) -> str:
        """_summary_
        :param question: _description_
        :type question: str
        :param context: _description_
        :type context: str
        :return: _description_
        :rtype: str
        """
        inputs = self._tokenizer(question, context, return_tensors="pt")
        inputs_onnx = {k: v.cpu().detach().numpy() for k, v in inputs.items()}
        logits = self._model_onnx.run(None, inputs_onnx)
        start_logits = logits[0]
        end_logits = logits[1]
        start_idx = np.argmax(start_logits)
        end_idx = np.argmax(end_logits) + 1
        answer_span = inputs[ExtractiveQA.INPUT_IDS][0][start_idx:end_idx]
        return self._tokenizer.decode(answer_span)

    def _clean(self, data):
        """_summary_
        :param data: _description_
        :type data: _type_
        """
        data = data[[Twitter.DATE, Twitter.TWEET, ExtractiveQA.ANSWER]]
        data = data[~data[ExtractiveQA.ANSWER].str.contains(ExtractiveQA.TAG_CLS)]
        data = data[data[ExtractiveQA.ANSWER] != ""]
        return data

    def _create_model_for_provider(self, provider: str = "CPUExecutionProvider"):
        """_summary_

        :param model_path: _description_
        :type model_path: str
        :param provider: _description_, defaults to "CPUExecutionnProvider"
        :type provider: str, optional
        :return: _description_
        :rtype: _type_
        """
        options = SessionOptions()
        options.intra_op_num_threads = 1
        options.graph_optimization_level = GraphOptimizationLevel.ORT_ENABLE_ALL
        session = InferenceSession(str(self._onnx_path), options, providers=[provider])
        session.disable_fallback()
        return session
