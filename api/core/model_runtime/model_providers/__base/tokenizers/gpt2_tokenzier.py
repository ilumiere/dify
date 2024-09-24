from os.path import abspath, dirname, join
from threading import Lock
from typing import Any

from transformers import GPT2Tokenizer as TransformerGPT2Tokenizer

_tokenizer = None
_lock = Lock()


class GPT2Tokenizer:
    """
    GPT2Tokenizer 类用于处理 GPT-2 模型的分词操作。
    该类提供了静态方法来获取 GPT-2 分词器实例，并计算给定文本的 token 数量。
    """

    @staticmethod
    def _get_num_tokens_by_gpt2(text: str) -> int:
        """
        使用 GPT-2 分词器计算给定文本的 token 数量。

        参数:
        text (str): 需要计算 token 数量的文本。

        返回值:
        int: 文本的 token 数量。
        """
        # 获取 GPT-2 分词器实例
        _tokenizer = GPT2Tokenizer.get_encoder()
        # 对输入文本进行分词，verbose=False 表示不输出详细信息
        tokens = _tokenizer.encode(text, verbose=False)
        # 返回分词后的 token 数量
        return len(tokens)

    @staticmethod
    def get_num_tokens(text: str) -> int:
        """
        获取给定文本的 token 数量。

        参数:
        text (str): 需要计算 token 数量的文本。

        返回值:
        int: 文本的 token 数量。
        """
        # 调用内部方法 _get_num_tokens_by_gpt2 计算 token 数量
        return GPT2Tokenizer._get_num_tokens_by_gpt2(text)

    @staticmethod
    def get_encoder() -> Any:
        """
        获取 GPT-2 分词器实例。

        返回值:
        Any: GPT-2 分词器实例。
        """
        global _tokenizer, _lock
        # 使用锁确保线程安全
        with _lock:
            # 如果分词器实例尚未初始化
            if _tokenizer is None:
                # 获取当前文件的绝对路径
                base_path = abspath(__file__)
                # 构建 GPT-2 分词器的路径
                gpt2_tokenizer_path = join(dirname(base_path), "gpt2")
                # 从预训练模型加载 GPT-2 分词器
                _tokenizer = TransformerGPT2Tokenizer.from_pretrained(gpt2_tokenizer_path)

            # 返回分词器实例
            return _tokenizer
