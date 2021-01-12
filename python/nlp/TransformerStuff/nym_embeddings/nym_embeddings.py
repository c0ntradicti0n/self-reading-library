from allennlp.common.checks import ConfigurationError
from overrides import overrides
from ampligraph.utils import restore_model

from allennlp.modules.token_embedders.token_embedder import TokenEmbedder
from allennlp.data import Vocabulary
from xnym_embeddings.time_tools import timeit_context
import torch
import numpy as np


@TokenEmbedder.register("nym_embedder")
class NymEmbedder (TokenEmbedder):
    """
    Represents a sequence of tokens as a relation based embeddings.


    Each sequence gets a vector of length vocabulary size, where the i'th entry in the vector
    corresponds to number of times the i'th token in the vocabulary appears in the sequence.
    By default, we ignore padding tokens.
    Parameters
    ----------
    vocab: ``Vocabulary``
    projection_dim : ``int``, optional (default = ``None``)
        if specified, will project the token ids to the knowledge embeddings
    ignore_oov : ``bool``, optional (default = ``False``)
        If true, we ignore the OOV token.
    """
    def __init__(self,
                 vocab: Vocabulary,
                 projection_dim: int = 10,
                 model_path:str=""
                 , ignore_oov=True):
        super(NymEmbedder, self).__init__()

        with timeit_context('initializing knowledge embedder'):
            self.vocab = vocab

            self._ignore_oov = ignore_oov
            oov_token = vocab._oov_token
            self._oov_idx = 0
            self.output_dim = projection_dim
            self.model = restore_model(model_name_path=model_path)

            self.oov_pad_vec = np.full(self.get_output_dim(), 1/self.get_output_dim())

    @overrides
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        inputs: ``torch.Tensor``
            Shape ``(batch_size, sequence_length)`` of word ids
            representing the current batch.
        Returns
        -------
        The distance position representations for the input sequence, shape
        ``(batch_size, vocab_size)``
        """
        input_array = inputs.cpu().detach().numpy().astype(int)
        return torch.FloatTensor([[self.model.get_embeddings(str(tok))
                                   if tok != self._oov_idx
                                   else self.oov_pad_vec
                                   for tok in sample]
                                  for sample in input_array])

    @overrides
    def get_output_dim(self) -> int:
        print (self.model.k * 2)
        return self.model.k

