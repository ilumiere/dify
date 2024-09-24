import time
from abc import abstractmethod
from typing import Optional

from pydantic import ConfigDict

from core.model_runtime.entities.model_entities import ModelType
from core.model_runtime.model_providers.__base.ai_model import AIModel


class ModerationModel(AIModel):
    """
    用于内容审核的模型类。

    该类继承自AIModel，主要用于处理内容审核任务。它定义了一个抽象方法_invoke，用于实际的模型调用，
    并提供了一个公共方法invoke，用于处理调用过程中的异常和计时。
    """

    model_type: ModelType = ModelType.MODERATION
    """
    模型类型，固定为ModelType.MODERATION，表示这是一个内容审核模型。
    """

    # pydantic configs
    model_config = ConfigDict(protected_namespaces=())
    """
    配置pydantic模型，设置protected_namespaces为空，表示不保护任何命名空间。
    """

    def invoke(self, model: str, credentials: dict, text: str, user: Optional[str] = None) -> bool:
        """
        调用内容审核模型。

        该方法首先记录调用开始时间，然后尝试调用实际的模型方法_invoke。如果调用过程中发生异常，
        则捕获异常并调用_transform_invoke_error方法进行处理。

        :param model: 模型名称，字符串类型。
        :param credentials: 模型凭证，字典类型。
        :param text: 需要审核的文本，字符串类型。
        :param user: 用户唯一ID，可选参数，字符串类型。
        :return: 如果文本安全则返回False，否则返回True。
        """
        self.started_at = time.perf_counter()
        """
        记录调用开始时间，使用time.perf_counter()获取当前时间。
        """

        try:
            return self._invoke(model, credentials, text, user)
            """
            尝试调用_invoke方法进行实际的模型调用。
            """
        except Exception as e:
            raise self._transform_invoke_error(e)
            """
            如果调用过程中发生异常，捕获异常并调用_transform_invoke_error方法进行处理。
            """

    @abstractmethod
    def _invoke(self, model: str, credentials: dict, text: str, user: Optional[str] = None) -> bool:
        """
        抽象方法，用于实际的模型调用。

        该方法需要在子类中实现，用于实际调用内容审核模型。

        :param model: 模型名称，字符串类型。
        :param credentials: 模型凭证，字典类型。
        :param text: 需要审核的文本，字符串类型。
        :param user: 用户唯一ID，可选参数，字符串类型。
        :return: 如果文本安全则返回False，否则返回True。
        """
        raise NotImplementedError
        """
        抛出NotImplementedError异常，表示该方法需要在子类中实现。
        """
