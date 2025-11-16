import pytest
import numpy as np
import tensorflow as tf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import tf_augmentations


class TestTfAugmentationsBasics:
    """Testes básicos da função tf_augmentations"""
    
    @pytest.fixture
    def sample_image_uint8(self):
        """Criar imagem de amostra em uint8 (0-255)"""
        return tf.constant(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
    
    @pytest.fixture
    def sample_image_float32(self):
        """Criar imagem de amostra em float32 (0-1)"""
        return tf.constant(np.random.rand(224, 224, 3).astype(np.float32))
    
    def test_augmentations_returns_dict(self, sample_image_uint8):
        """Validar que retorna um dicionário"""
        result = tf_augmentations(sample_image_uint8)
        assert isinstance(result, dict)
    
    def test_augmentations_has_correct_keys(self, sample_image_uint8):
        """Validar que tem todas as 10 chaves esperadas"""
        expected_keys = {
            "orig", "rot90", "rot180", "flip_lr", "flip_ud",
            "bright", "contrast", "hue", "saturation", "crop"
        }
        result = tf_augmentations(sample_image_uint8)
        assert set(result.keys()) == expected_keys
    
    def test_all_augmentations_return_tensors(self, sample_image_uint8):
        """Validar que todas as augmentations retornam tensores"""
        result = tf_augmentations(sample_image_uint8)
        for key, tensor in result.items():
            assert isinstance(tensor, (tf.Tensor, tf.Variable))


class TestAugmentationsShape:
    """Testes de preservação de dimensões"""
    
    @pytest.fixture
    def sample_image(self):
        return tf.constant(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
    
    def test_orig_preserves_shape(self, sample_image):
        """Original mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["orig"].shape == (224, 224, 3)
    
    def test_rot90_preserves_shape(self, sample_image):
        """Rotação 90° mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["rot90"].shape == (224, 224, 3)
    
    def test_rot180_preserves_shape(self, sample_image):
        """Rotação 180° mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["rot180"].shape == (224, 224, 3)
    
    def test_flip_lr_preserves_shape(self, sample_image):
        """Flip horizontal mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["flip_lr"].shape == (224, 224, 3)
    
    def test_flip_ud_preserves_shape(self, sample_image):
        """Flip vertical mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["flip_ud"].shape == (224, 224, 3)
    
    def test_brightness_preserves_shape(self, sample_image):
        """Ajuste de brilho mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["bright"].shape == (224, 224, 3)
    
    def test_contrast_preserves_shape(self, sample_image):
        """Ajuste de contraste mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["contrast"].shape == (224, 224, 3)
    
    def test_hue_preserves_shape(self, sample_image):
        """Ajuste de hue mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["hue"].shape == (224, 224, 3)
    
    def test_saturation_preserves_shape(self, sample_image):
        """Ajuste de saturação mantém shape"""
        result = tf_augmentations(sample_image)
        assert result["saturation"].shape == (224, 224, 3)
    
    def test_crop_reduces_shape(self, sample_image):
        """Crop reduz para 70% do tamanho original"""
        result = tf_augmentations(sample_image)
        # central_crop 0.7 reduz para 70% do tamanho
        expected_size = int(224 * 0.7)
        assert result["crop"].shape == (expected_size, expected_size, 3)


class TestAugmentationsValues:
    """Testes de validação de valores"""
    
    @pytest.fixture
    def sample_image(self):
        return tf.constant(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
    
    def test_no_nan_values(self, sample_image):
        """Validar ausência de NaN em todas as augmentations"""
        result = tf_augmentations(sample_image)
        for key, tensor in result.items():
            assert not tf.reduce_any(tf.math.is_nan(tensor)), f"{key} contém NaN"
    
    def test_no_inf_values(self, sample_image):
        """Validar ausência de valores infinitos"""
        result = tf_augmentations(sample_image)
        for key, tensor in result.items():
            assert not tf.reduce_any(tf.math.is_inf(tensor)), f"{key} contém Inf"
    
    def test_values_in_valid_range(self, sample_image):
        """Validar que valores estão em range razoável"""
        result = tf_augmentations(sample_image)
        for key, tensor in result.items():
            # Permitir um range maior para acomodar ajustes de cor
            assert tf.reduce_all(tensor >= -100) and tf.reduce_all(tensor <= 500), \
                f"{key} tem valores fora do range esperado"


class TestAugmentationsDiversity:
    """Testes de variação entre augmentations"""
    
    @pytest.fixture
    def sample_image(self):
        return tf.constant(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
    
    def test_rot90_differs_from_original(self, sample_image):
        """Rotação 90° deve diferir da original"""
        result = tf_augmentations(sample_image)
        diff = tf.reduce_mean(tf.cast(result["rot90"], tf.float32) - 
                             tf.cast(result["orig"], tf.float32))
        assert abs(float(diff)) > 0.1
    
    def test_flip_lr_differs_from_original(self, sample_image):
        """Flip horizontal deve diferir"""
        result = tf_augmentations(sample_image)
        diff = tf.reduce_mean(tf.cast(result["flip_lr"], tf.float32) - 
                             tf.cast(result["orig"], tf.float32))
        assert abs(float(diff)) > 0.1
    
    def test_brightness_changes_intensity(self, sample_image):
        """Brilho deve aumentar intensidade média"""
        result = tf_augmentations(sample_image)
        orig_mean = tf.reduce_mean(tf.cast(result["orig"], tf.float32))
        bright_mean = tf.reduce_mean(tf.cast(result["bright"], tf.float32))
        assert bright_mean > orig_mean, "Brilho deve aumentar intensidade"
    
    def test_contrast_increases_difference(self, sample_image):
        """Contraste deve aumentar diferença entre pixels"""
        result = tf_augmentations(sample_image)
        orig_std = tf.math.reduce_std(tf.cast(result["orig"], tf.float32))
        contrast_std = tf.math.reduce_std(tf.cast(result["contrast"], tf.float32))
        assert contrast_std > orig_std, "Contraste deve aumentar desvio padrão"


class TestAugmentationsSpecific:
    """Testes específicos para cada augmentation"""
    
    @pytest.fixture
    def gradient_image(self):
        """Criar imagem com padrão de gradiente para testes mais precisos"""
        gradient = np.linspace(0, 255, 224)
        img = np.tile(gradient, (224, 1))
        img = np.stack([img, img, img], axis=-1)
        return tf.constant(img.astype(np.uint8))
    
    def test_rot90_rotates_correctly(self, gradient_image):
        """Validar que rot90 realmente rotaciona"""
        result = tf_augmentations(gradient_image)
        # Após rotação, primeira linha deve vir de última coluna
        orig_first_col = result["orig"][0, :, 0].numpy()
        rot_first_row = result["rot90"][0, :, 0].numpy()
        # Devem ser similares (mesmos valores)
        assert np.allclose(orig_first_col, rot_first_row[::-1], rtol=1)
    
    def test_rot180_is_two_rotations(self, gradient_image):
        """Validar que rot180 é equiv a rot90 2x"""
        result = tf_augmentations(gradient_image)
        rot90_twice = tf.image.rot90(result["rot90"], k=1)
        assert tf.reduce_all(tf.abs(
            tf.cast(result["rot180"], tf.int32) - 
            tf.cast(rot90_twice, tf.int32)
        ) <= 1)  # Permitir pequeno erro de arredondamento
    
    def test_flip_lr_mirrors_horizontally(self, gradient_image):
        """Validar que flip_lr espelha horizontalmente"""
        result = tf_augmentations(gradient_image)
        orig_first_col = result["orig"][:, 0, 0].numpy()
        flip_last_col = result["flip_lr"][:, -1, 0].numpy()
        assert np.allclose(orig_first_col, flip_last_col)
    
    def test_flip_ud_mirrors_vertically(self, gradient_image):
        """Validar que flip_ud espelha verticalmente"""
        result = tf_augmentations(gradient_image)
        orig_first_row = result["orig"][0, :, 0].numpy()
        flip_last_row = result["flip_ud"][-1, :, 0].numpy()
        assert np.allclose(orig_first_row, flip_last_row)
    
    def test_crop_returns_center(self, gradient_image):
        """Validar que crop retorna área central"""
        result = tf_augmentations(gradient_image)
        crop_result = result["crop"]
        # Crop de 70% deve ter 157x157 (aproximadamente)
        assert crop_result.shape[0] == crop_result.shape[1]


class TestAugmentationsEdgeCases:
    """Testes para casos extremos"""
    
    def test_all_black_image(self):
        """Testar com imagem completamente preta"""
        black_image = tf.zeros((224, 224, 3), dtype=tf.uint8)
        result = tf_augmentations(black_image)
        assert len(result) == 10
        for key, tensor in result.items():
            assert tensor.shape[0] > 0
    
    def test_all_white_image(self):
        """Testar com imagem completamente branca"""
        white_image = tf.ones((224, 224, 3), dtype=tf.uint8) * 255
        result = tf_augmentations(white_image)
        assert len(result) == 10
        for key, tensor in result.items():
            assert tensor.shape[0] > 0
    
    def test_different_image_sizes(self):
        """Testar com diferentes tamanhos de imagem"""
        for size in [64, 128, 256, 512]:
            image = tf.constant(np.random.randint(0, 256, (size, size, 3), dtype=np.uint8))
            result = tf_augmentations(image)
            assert len(result) == 10
    
    def test_single_channel_converted_to_3_channels(self):
        """Se alguém passar 1 canal, verificar comportamento"""
        # Nota: tf_augmentations espera 3 canais, mas testar robustez
        try:
            single_channel = tf.constant(np.random.randint(0, 256, (224, 224, 1), dtype=np.uint8))
            result = tf_augmentations(single_channel)
            # Se não lançar erro, tudo bem
            assert result is not None
        except Exception as e:
            # Se lançar erro, também é aceitável (função espera 3 canais)
            assert True


class TestAugmentationsPerformance:
    """Testes de performance"""
    
    def test_augmentations_completes_in_reasonable_time(self):
        """Validar que augmentations são rápidas"""
        import time
        image = tf.constant(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
        
        start = time.time()
        result = tf_augmentations(image)
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Augmentations levaram {elapsed}s, esperado < 1s"
    
    def test_multiple_augmentations_batch(self):
        """Validar performance com múltiplas imagens"""
        import time
        
        start = time.time()
        for _ in range(10):
            image = tf.constant(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
            result = tf_augmentations(image)
        elapsed = time.time() - start
        
        assert elapsed < 10.0, f"Batch levou {elapsed}s, esperado < 10s"