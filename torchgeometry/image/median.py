from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


def _compute_binary_kernel(window_size: Tuple[int, int]) -> torch.Tensor:
    r"""Creates a binary kernel to extract the patches. If the window size
    is HxW will create a (H*W)xHxW kernel.
    """
    window_range: int = window_size[0] * window_size[1]
    kernel: torch.Tensor = torch.zeros(window_range, window_range)
    for i in range(window_range):
        kernel[i, i] += 1.0
    return kernel.view(window_range, 1, window_size[0], window_size[1])


def _compute_zero_padding(kernel_size: Tuple[int, int]) -> Tuple[int, int]:
    r"""Utility function that computes zero padding tuple."""
    computed: Tuple[int, ...] = tuple([(k - 1) // 2 for k in kernel_size])
    return computed[0], computed[1]


class MedianBlur(nn.Module):
    r"""Blurs an image using the median filter.

    Args:
        kernel_size (Tuple[int, int]): the blurring kernel size.

    Returns:
        torch.Tensor: the blurred input tensor.

    Shape:
        - Input: :math:`(B, C, H, W)`
        - Output: :math:`(B, C, H, W)`

    Example:
        >>> input = torch.rand(2, 4, 5, 7)
        >>> blur = tgm.image.MedianBlur((3, 3))
        >>> output = blur(input)  # 2x4x5x7
    """

    def __init__(self, kernel_size: Tuple[int, int]) -> None:
        super(MedianBlur, self).__init__()
        self.kernel: torch.Tensor = _compute_binary_kernel(kernel_size)
        self.padding: Tuple[int, int] = _compute_zero_padding(kernel_size)

    def forward(self, input: torch.Tensor):  # type: ignore
        if not torch.is_tensor(input):
            raise TypeError("Input type is not a torch.Tensor. Got {}"
                            .format(type(input)))
        if not len(input.shape) == 4:
            raise ValueError("Invalid input shape, we expect BxCxHxW. Got: {}"
                             .format(input.shape))
        # prepare kernel
        b, c, h, w = input.shape
        tmp_kernel: torch.Tensor = self.kernel.to(input.device).to(input.dtype)
        kernel: torch.Tensor = tmp_kernel.repeat(c, 1, 1, 1)

        # map the local window to single vector
        features: torch.Tensor = F.conv2d(
            input, kernel, padding=self.padding, stride=1, groups=c)
        features = features.view(b, c, -1, h, w)  # BxCx(K_h * K_w)xHxW

        # compute the median along the feature axis
        median: torch.Tensor = torch.median(features, dim=2)[0]
        return median


# functiona api


def median_blur(input: torch.Tensor,
                kernel_size: Tuple[int, int]) -> torch.Tensor:
    r"""Blurs an image using the median filter.

    See :class:`~torchgeometry.image.MedianBlur` for details.
    """
    return MedianBlur(kernel_size)(input)
