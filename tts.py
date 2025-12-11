import pyttsx3
import os

class CoquiTTS:
    def __init__(self):
        self.voices_list = {
            "female": 1,
            "male": 0
        }
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
    
    def get_model(self, voice: str):
        if voice not in self.voices_list:
            return {"status": "error", "message": f"Voice '{voice}' not supported"}
        return voice
    
    def generate_speech(self, text: str, voice: str = "female", output_file: str = "output.wav"):
        try:
            if not text or len(text.strip()) == 0:
                return {"status": "error", "message": "Text cannot be empty"}
            
            voice_check = self.get_model(voice)
            
            if isinstance(voice_check, dict) and "error" in voice_check.get("status", ""):
                return voice_check
            
            voices = self.engine.getProperty('voices')
            voice_id = self.voices_list[voice]
            
            if voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
            
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                return {
                    "status": "success",
                    "audio_file": output_file,
                    "file_size": file_size,
                    "text": text,
                    "voice": voice
                }
            else:
                return {"status": "error", "message": "Failed to create audio file"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_available_voices(self):
        return {
            "status": "success",
            "voices": list(self.voices_list.keys())
        }
    
    def batch_generate(self, requests: list):
        results = []
        for req in requests:
            result = self.generate_speech(
                text=req.get("text"),
                voice=req.get("voice", "female"),
                output_file=req.get("output_file", "output.wav")
            )
            results.append(result)
        return {"status": "success", "results": results}


def main():
    print("Initializing pyttsx3 TTS...")
    tts = CoquiTTS()
    
    while True:
        print("\n" + "="*50)
        print("COQUI TTS - LIVE TESTING")
        print("="*50)
        print("1. Generate Speech (Single)")
        print("2. Get Available Voices")
        print("3. Batch Generation")
        print("4. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            text = input("Enter text to convert: ").strip()
            voices = tts.get_available_voices()["voices"]
            print(f"Available voices: {voices}")
            voice = input(f"Choose voice ({'/'.join(voices)}): ").strip()
            output = input("Enter output file name (default: output.wav): ").strip() or "output.wav"
            
            print("\nGenerating speech...")
            response = tts.generate_speech(text, voice, output)
            print(f"Response: {response}\n")
            
            if response["status"] == "success":
                print(f"✓ Audio saved to: {response['audio_file']}")
                print(f"✓ File size: {response['file_size']} bytes")
        
        elif choice == "2":
            voices = tts.get_available_voices()
            print(f"\n{voices}\n")
        
        elif choice == "3":
            count = int(input("How many requests? ").strip())
            requests = []
            
            for i in range(count):
                print(f"\n--- Request {i+1} ---")
                text = input("Enter text: ").strip()
                voices = tts.get_available_voices()["voices"]
                voice = input(f"Choose voice ({'/'.join(voices)}): ").strip()
                output = input("Output file name (default: output_{i}.wav): ").strip() or f"output_{i}.wav"
                
                requests.append({"text": text, "voice": voice, "output_file": output})
            
            print("\nGenerating batch...")
            response = tts.batch_generate(requests)
            print(f"Response: {response}\n")
        
        elif choice == "4":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice! Try again.")

if __name__ == "__main__":
    main()