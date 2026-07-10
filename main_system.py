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
        self.auth_token = os.getenv("SUNO_AUTH_TOKEN")
        self.browser_token = os.getenv("SUNO_BROWSER_TOKEN")
        self.device_id = os.getenv("SUNO_DEVICE_ID")

        if not all([self.auth_token, self.browser_token, self.device_id]):
            print("Warning: Suno authentication environment variables are missing.")

        self.suno = SunoAutoGenerator(self.auth_token, self.browser_token, self.device_id) if self.auth_token else None
        self.prompter = EnhancedPrompter()
        self.analyzer = MusicAnalyzer()
        self.repair = SelfHealingAI()
        self.song_count = 8
        self.output_dir = "generated_songs"
        os.makedirs(self.output_dir, exist_ok=True)
        self.report_file = "daily_report.md"

    def run_daily_cycle(self):
        print(f"Starting daily generation cycle at {datetime.now()}")

        if self.repair.check_health() != "OK":
            self.repair.handle_error("System health check failed at startup")

        generated_files = []

        for i in range(self.song_count):
            print(f"\n--- Generating Song {i+1}/{self.song_count} ---")

            try:
                base_idea = (
                    "instrumental only, no vocals, smooth jazz, cafe background music, "
                    "87 BPM, clean production, no crackle, no tape hiss, no noise artifacts, "
                    "polished and unobtrusive"
                )
                prompt_package = self.prompter.generate_full_prompt_package(base_idea)

                style_tags = prompt_package['prompt']
                title = self.prompter.generate_timestamp_title("CafeBGM")

                if not self.suno:
                    print("Suno engine not initialized. Skipping generation.")
                    continue

                generate_ids = self.suno.generate_song(style_tags, title, instrumental=True)
                completed_songs = self.suno.wait_for_song_completion(generate_ids)

                if not completed_songs:
                    print(f"No songs completed for cycle {i+1}")
                    continue

                for song in completed_songs:
                    timestamp_title = self.prompter.generate_timestamp_title("CafeBGM")
                    file_path = os.path.join(self.output_dir, f"{timestamp_title}.mp3")

                    audio_url = song.get("audio_url")
                    if not audio_url:
                        print(f"No audio_url for song, skipping download")
                        continue

                    download_success = self.suno.download_song(audio_url, file_path)

                    if download_success:
                        analysis_result = self.analyzer.analyze_audio(file_path)
                        score = analysis_result.get("quality_score", 0.5)
                        feedback = analysis_result.get("feedback", "")

                        params_used = {
                            "weirdness": prompt_package['weirdness'],
                            "style_influence": prompt_package['style_influence']
                        }
                        self.prompter.update_learning(score, params_used, feedback)

                        generated_files.append({
                            "path": file_path,
                            "title": timestamp_title,
                            "score": score,
                            "feedback": feedback
                        })
                        print(f"Successfully generated and learned from: {timestamp_title}")
                        break
                    else:
                        print(f"Failed to download song: {timestamp_title}")

            except Exception as e:
                print(f"Error in cycle {i+1}: {e}")
                self.repair.handle_error(e)
                continue

        self.create_report(generated_files)

    def create_report(self, files):
        """メール送信用のマークダウンレポートを作成"""
        report_content = f"# AI Music Generation Daily Report ({datetime.now().strftime('%Y-%m-%d')})\n\n"

        if not files:
            report_content += "残念ながら、本日の楽曲生成は失敗しました。認証情報の有効期限やSuno AIのステータスを確認してください。\n"
        else:
            report_content += f"本日は合計 **{len(files)}曲** の生成に成功しました。\n\n"
            report_content += "| 楽曲名 | 品質スコア | フィードバック |\n"
            report_content += "| :--- | :--- | :--- |\n"
            for f in files:
                report_content += f"| {f['title']} | {f['score']:.2f} | {f['feedback']} |\n"
