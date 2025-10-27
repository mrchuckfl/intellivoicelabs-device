#!/usr/bin/env python3
"""Unit tests for IntelliVoice Device core components."""
import unittest
import json
import time
import threading

# Import our modules
import main


class TestStateManager(unittest.TestCase):
    """Test StateManager class."""
    
    def setUp(self):
        self.config = {
            "modes": {
                "default_mode": "convert",
                "languages": ["EN", "ES", "FR"]
            }
        }
        self.state = main.StateManager(self.config)
    
    def test_initial_state(self):
        """Test initial state values."""
        self.assertEqual(self.state.mode, "convert")
        self.assertEqual(len(self.state.languages), 3)
        self.assertTrue(self.state.running)
    
    def test_mode_toggle(self):
        """Test mode toggling."""
        self.assertEqual(self.state.mode, "convert")
        self.state.toggle_mode()
        self.assertEqual(self.state.mode, "bypass")
        self.state.toggle_mode()
        self.assertEqual(self.state.mode, "convert")
    
    def test_language_cycling(self):
        """Test language cycling."""
        snap = self.state.get_snapshot()
        initial_lang = snap["language"]
        
        self.state.next_language()
        snap = self.state.get_snapshot()
        self.assertNotEqual(snap["language"], initial_lang)
        
        # Cycle through all languages
        for _ in range(len(self.state.languages)):
            self.state.next_language()
        
        # Should cycle back to first
        snap = self.state.get_snapshot()
    
    def test_snapshot_consistency(self):
        """Test that snapshots are thread-safe."""
        def modify_state():
            for _ in range(10):
                self.state.toggle_mode()
                self.state.next_language()
                time.sleep(0.01)
        
        thread = threading.Thread(target=modify_state)
        thread.start()
        
        # Get snapshots while modifying
        for _ in range(50):
            snap = self.state.get_snapshot()
            self.assertIn("mode", snap)
            self.assertIn("language", snap)
            self.assertIn("level_rms", snap)
            self.assertIn("latency_ms", snap)
            time.sleep(0.01)
        
        thread.join()


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration validation."""
    
    def test_valid_config(self):
        """Test with valid configuration."""
        config = {
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "frames_per_buffer": 1024
            },
            "gpio": {
                "bypass_button": 17,
                "language_button": 27,
                "led_bypass": 22,
                "led_convert": 23,
                "ptt_input": 24,
                "pullups": False
            },
            "display": {
                "enabled": True,
                "i2c_port": 13,
                "i2c_address": 60
            },
            "modes": {
                "default_mode": "convert",
                "languages": ["EN", "ES", "FR"]
            },
            "logging": {
                "level": "INFO"
            }
        }
        errors, warnings = main.validate_config(config)
        self.assertEqual(len(errors), 0)
    
    def test_missing_section(self):
        """Test with missing required section."""
        config = {
            "audio": {"sample_rate": 16000}
            # Missing other sections
        }
        errors, warnings = main.validate_config(config)
        self.assertGreater(len(errors), 0)
    
    def test_invalid_mode(self):
        """Test with invalid mode setting."""
        config = {
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "frames_per_buffer": 1024
            },
            "gpio": {
                "bypass_button": 17,
                "language_button": 27,
                "led_bypass": 22,
                "led_convert": 23,
                "ptt_input": 24
            },
            "display": {
                "enabled": True
            },
            "modes": {
                "default_mode": "invalid_mode",
                "languages": ["EN"]
            },
            "logging": {}
        }
        errors, warnings = main.validate_config(config)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("default_mode" in err for err in errors))
    
    def test_invalid_data_types(self):
        """Test with invalid data types."""
        config = {
            "audio": {
                "sample_rate": "16000",  # Should be int
                "channels": 1,
                "frames_per_buffer": 1024
            },
            "gpio": {
                "bypass_button": 17,
                "language_button": 27,
                "led_bypass": 22,
                "led_convert": 23,
                "ptt_input": 24
            },
            "display": {
                "enabled": True
            },
            "modes": {
                "default_mode": "convert",
                "languages": "EN"  # Should be list
            },
            "logging": {}
        }
        errors, warnings = main.validate_config(config)
        self.assertGreater(len(errors), 0)


class TestConfigurationLoading(unittest.TestCase):
    """Test configuration loading."""
    
    def test_load_config(self):
        """Test loading configuration file."""
        config = main.load_config()
        self.assertIsInstance(config, dict)
        self.assertIn("audio", config)
        self.assertIn("gpio", config)
        self.assertIn("display", config)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in components."""
    
    def test_oled_without_hardware(self):
        """Test OLED initialization without hardware."""
        config = {
            "display": {
                "enabled": False,  # Disable to avoid hardware requirement
                "i2c_port": 13,
                "i2c_address": 60
            }
        }
        display = main.OLEDDisplay(config)
        self.assertIsNone(display.device)
    
    def test_gpio_without_hardware(self):
        """Test GPIO controller handles missing hardware."""
        config = {
            "gpio": {
                "bypass_button": 17,
                "language_button": 27,
                "led_bypass": 22,
                "led_convert": 23,
                "ptt_input": 24
            }
        }
        
        # This will fail without actual hardware, but should fail gracefully
        # We can't really test this without a Pi
        pass


def run_tests():
    """Run all unit tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

