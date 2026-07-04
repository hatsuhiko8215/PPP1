import os
import time
import json
from datetime import datetime
from suno_engine import SunoAutoGenerator
from prompter import EnhancedPrompter
from analyzer import MusicAnalyzer
from repair_unit import SelfHealingAI

class LofiMusicSystem:
    def __init__(self):
        self.cookie = os.getenv("SUNO_COOKIE")
        if not self.cookie:
            print("Warning: SUNO_COOKIE not found in environment variables.")
        
        self.suno = SunoAutoGenerator(self.cookie) if self.cookie else None
        self.prompter = EnhancedPrompter()
        self.analyzer = MusicAnalyzer()
        self.repair = SelfHealingAI()
        self.song_count = 8
        self.output_dir = "generated_songs"
        os.makedirs(self.output_dir, exist_ok=True)

    def run_daily_cycle(self):
        print(f"Starting daily generation cycle at {datetime.now()}")
        
        if self.repair.check_health() != "OK":
            self.repair.handle_error("System health check failed at startup")

        generated_files = []
        
        for i in range(self.song_count):
            print(f"\n--- Generating Song {i+1}/{self.song_count} ---")
            
            try:
                base_idea = "Chill cafe BGM, mellow piano, nostalgic atmosphere"
                prompt_package = self.prompter.generate_full_prompt_package(base_idea)
                
                full_prompt = f"{prompt_package['prompt']} --weirdness {prompt_package['weirdness']} --style_influence {prompt_package['style_influence']}"
                
                if not self.suno:
                    print("Suno engine not initialized. Skipping generation.")
                    continue

                generate_ids = self.suno.generate_song(full_prompt)
                completed_songs = self.suno.wait_for_song_completion(generate_ids)
                
                for song in completed_songs:
                    timestamp_title = self.prompter.generate_timestamp_title(f"Song_{song['id']}")
                    file_path = os.path.join(self.output_dir, f"{timestamp_title}.mp3")
                    
                    self.suno.download_song(song['audio_url'], file_path)
                    
                    analysis_result = self.analyzer.analyze_audio(file_path)
                    score = analysis_result.get("quality_score", 0.5)
                    feedback = analysis_result.get("feedback", "")
                    
                    params_used = {
                        "weirdness": prompt_package['weirdness'],
                        "style_influence": prompt_package['style_influence']
                    }
                    self.prompter.update_learning(score, params_used, feedback)
                    
                    generated_files.append(file_path)
                    print(f"Successfully generated and learned from: {timestamp_title}")
                    break 
                
            except Exception as e:
                print(f"Error in cycle {i+1}: {e}")
                self.repair.handle_error(e)
                continue

        self.report_results(generated_files)

    def report_results(self, files):
        print(f"\nCycle complete. Generated {len(files)} songs.")
        for f in files:
            print(f"Saved: {os.path.basename(f)}")

if __name__ == "__main__":
    system = LofiMusicSystem()
    system.run_daily_cycle()
