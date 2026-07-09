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
        self.report_file = "daily_report.md"

    def run_daily_cycle(self):
        print(f"Starting daily generation cycle at {datetime.now()}")
        
        if self.repair.check_health() != "OK":
            self.repair.handle_error("System health check failed at startup")

        generated_files = []
        
        for i in range(self.song_count):
            print(f"\n--- Generating Song {i+1}/{self.song_count} ---")
            
            try:
                # TikTokトレンドを意識したベースアイデア
                base_idea = "TikTok trend, viral Lo-fi, smooth transition, high quality"
                prompt_package = self.prompter.generate_full_prompt_package(base_idea)
                
                # パラメータ学習を反映したフルプロンプト
                full_prompt = f"{prompt_package['prompt']} --weirdness {prompt_package['weirdness']} --style_influence {prompt_package['style_influence']}"
                
                if not self.suno:
                    print("Suno engine not initialized. Skipping generation.")
                    continue

                generate_ids = self.suno.generate_song(full_prompt)
                completed_songs = self.suno.wait_for_song_completion(generate_ids)
                
                if not completed_songs:
                    print(f"No songs completed for cycle {i+1}")
                    continue

                for song in completed_songs:
                    # 要件通りの命名規則（西暦_日付_時間）
                    timestamp_title = self.prompter.generate_timestamp_title(f"Lofi_BGM")
                    file_path = os.path.join(self.output_dir, f"{timestamp_title}.mp3")
                    
                    # 楽曲のダウンロード
                    download_success = self.suno.download_song(song['audio_url'], file_path)
                    
                    if download_success:
                        # 楽曲の分析と学習
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
            report_content += "残念ながら、本日の楽曲生成は失敗しました。Cookieの有効期限やSuno AIのステータスを確認してください。\n"
        else:
            report_content += f"本日は合計 **{len(files)}曲** の生成に成功しました。\n\n"
            report_content += "| 楽曲名 | 品質スコア | フィードバック |\n"
            report_content += "| :--- | :--- | :--- |\n"
            for f in files:
                report_content += f"| {f['title']} | {f['score']:.2f} | {f['feedback']} |\n"
            
            report_content += "\n## 学習の進捗\n"
            report_content += "システムは生成ごとにパラメータ（Weirdness, Style Influence）を調整し、Lo-fi特有のクラッチ音を最小限に抑えるプロンプトを学習しています。\n"

        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report created: {self.report_file}")

if __name__ == "__main__":
    system = LofiMusicSystem()
    system.run_daily_cycle()
