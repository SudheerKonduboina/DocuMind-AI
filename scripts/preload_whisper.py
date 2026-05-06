"""
Preload Whisper Model
Downloads the Whisper model before demo to avoid delay during transcription.
Run this script before starting the backend server for demo.
"""
import whisper
import sys


def preload_whisper_model(model_name="base"):
    """
    Preload the Whisper model to ensure it's downloaded before demo.
    
    Args:
        model_name: Whisper model size (tiny, base, small, medium, large)
    """
    print(f"Preloading Whisper model: {model_name}")
    print("This may take a few minutes on first run...")
    
    try:
        model = whisper.load_model(model_name)
        print(f"✓ Whisper model '{model_name}' loaded successfully!")
        print(f"Model size: {model_name}")
        return model
    except Exception as e:
        print(f"✗ Error loading Whisper model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Default to 'base' model for demo (good balance of speed/accuracy)
    model_name = sys.argv[1] if len(sys.argv) > 1 else "base"
    
    preload_whisper_model(model_name)
    print("\nWhisper model is ready for demo!")
