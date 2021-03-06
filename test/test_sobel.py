import pytest

import torch
import torchgeometry as tgm
from torch.testing import assert_allclose
from torch.autograd import gradcheck

import utils  # test utils


class TestSpatialGradient:
    def test_shape(self):
        inp = torch.zeros(1, 3, 4, 4)
        sobel = tgm.image.SpatialGradient()
        assert sobel(inp).shape == (1, 3, 2, 4, 4)

    def test_shape_batch(self):
        inp = torch.zeros(2, 6, 4, 4)
        sobel = tgm.image.SpatialGradient()
        assert sobel(inp).shape == (2, 6, 2, 4, 4)

    def test_edges(self):
        inp = torch.tensor([[[
            [0., 1., 0.],
            [1., 1., 1.],
            [0., 1., 0.],
        ]]])

        expected = torch.tensor([[[[
            [3., 0., -3.],
            [4., 0., -4.],
            [3., 0., -3.],
        ], [
            [3., 4., 3.],
            [0., 0., 0.],
            [-3., -4., -3.],
        ]]]])

        edges = tgm.image.spatial_gradient(inp)
        assert_allclose(edges, expected)

    def test_gradcheck(self):
        batch_size, channels, height, width = 1, 2, 5, 4
        img = torch.rand(batch_size, channels, height, width)
        img = utils.tensor_to_gradcheck_var(img)  # to var
        assert gradcheck(tgm.image.spatial_gradient, (img,),
                         raise_exception=True)

    def test_jit(self):
        @torch.jit.script
        def op_script(input):
            return tgm.image.spatial_gradient(input)
        img = torch.rand(2, 3, 4, 5)
        actual = op_script(img)
        expected = tgm.image.spatial_gradient(img)
        assert_allclose(actual, expected)


class TestSobel:
    def test_shape(self):
        inp = torch.zeros(1, 3, 4, 4)
        sobel = tgm.image.Sobel()
        assert sobel(inp).shape == (1, 3, 4, 4)

    def test_shape_batch(self):
        inp = torch.zeros(3, 2, 4, 4)
        sobel = tgm.image.Sobel()
        assert sobel(inp).shape == (3, 2, 4, 4)

    def test_magnitude(self):
        inp = torch.tensor([[[
            [0., 1., 0.],
            [1., 1., 1.],
            [0., 1., 0.],
        ]]])

        expected = torch.tensor([[[
            [4.2426, 4.00, 4.2426],
            [4.0000, 0.00, 4.0000],
            [4.2426, 4.00, 4.2426],
        ]]])

        edges = tgm.image.sobel(inp)
        assert_allclose(edges, expected)

    def test_gradcheck(self):
        batch_size, channels, height, width = 1, 2, 5, 4
        img = torch.rand(batch_size, channels, height, width)
        img = utils.tensor_to_gradcheck_var(img)  # to var
        assert gradcheck(tgm.image.sobel, (img,), raise_exception=True)

    def test_jit(self):
        @torch.jit.script
        def op_script(input):
            return tgm.image.sobel(input)
        img = torch.rand(2, 3, 4, 5)
        actual = op_script(img)
        expected = tgm.image.sobel(img)
        assert_allclose(actual, expected)
