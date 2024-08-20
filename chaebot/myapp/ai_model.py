import yt_dlp
import subprocess
import os
import essentia
from essentia.standard import MonoLoader, RhythmExtractor2013
from spleeter.separator import Separator
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
from music21 import stream, note, chord, tempo, metadata, instrument, environment
import torch
import torch.nn as nn
from torchvision import models
import re
import torchvision.transforms as transforms
import torch.nn.functional as F
import shutil


class EfficientNetModel(nn.Module):
    def __init__(self, num_classes):
        super(EfficientNetModel, self).__init__()
        self.base_model = models.efficientnet_b3(pretrained=True)
        # 첫 번째 Conv2d 레이어의 입력 채널을 1로 변경
        self.base_model.features[0][0] = nn.Conv2d(1, 40, kernel_size=(3, 3), stride=(2, 2), bias=False)
        self.base_model.classifier[1] = nn.Linear(self.base_model.classifier[1].in_features, num_classes)

    def forward(self, x):
        return torch.sigmoid(self.base_model(x))



class chaebot:
    def __init__(self, mp3_file_path = None, youtube_link = None): # mp3_file: mp3 경로 / youtube_link: youtube 링크 문자열
        self.mp3_file_path = mp3_file_path
        self.youtube_link = youtube_link
        self.bpm = None
        self.drum_wav_file_path = None
        self.chunked_file_path = None
        self.chunk_length_ms = 0
        self.predictions = []
        self.title = "my music"

    def save_mp3_file_path(self):  # mp3 파일을 지정된 경로에 저장
        # mp3 파일을 지정된 경로에 저장
        save_path = "music.mp3"
        with open(save_path, 'wb') as f:
            f.write(self.mp3_file_path)

        # mp3 파일 경로 업데이트
        self.mp3_file_path = save_path

        # 그리고 악보의 title을 미리 지정 (확장자를 제거한 파일 이름만 추출)
        self.title = os.path.splitext(self.mp3_file_path)[0][:20]

    def save_youtube_link_to_mp3(self): # 유튜브 영상을 mp3 파일로 변환
        # yt-dlp를 사용하여 오디오 다운로드
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'output.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.youtube_link, download=True)
            file_name = ydl.prepare_filename(info_dict)

            # 유튜브 동영상 제목 가져오기
            video_title = info_dict.get('title', 'unknown_title')

            # 제목이 20자 이상이면 20자까지만 저장
            self.title = video_title[:20]

        # 다운로드된 파일을 mp3로 변환
        save_path = 'music.mp3'
        subprocess.run(['ffmpeg', '-i', file_name, '-q:a', '0', '-map', 'a', save_path])

        # 원본 오디오 파일 삭제
        os.remove(file_name)

        # mp3 파일 경로 업데이트
        self.mp3_file_path = save_path

    def extract_bpm(self): # wav의 bpm을 추출합니다
        # 오디오 파일 로드
        loader = MonoLoader(filename=self.mp3_file_path)
        audio = loader()

        # bpm 추출 및 저장
        rhythm_extractor = RhythmExtractor2013()
        bpm, ticks, confidence, estimates, bpmIntervals = rhythm_extractor(audio)
        self.bpm = bpm

    def transform_wav_to_drum(self):  # wav를 드럼으로 변환
        separator = Separator('spleeter:4stems')

        # 입력 파일 경로와 출력 디렉토리 설정
        input_audio_path = self.mp3_file_path
        output_directory = "./"

        # 파일 분리
        separator.separate_to_file(input_audio_path, output_directory)

        # 드럼 파일 경로 설정
        self.drum_wav_file_path = os.path.join("music/", 'drums.wav')

    def cut_drum_intro(self):
        # 드럼 트랙 로드
        y, sr = librosa.load(self.drum_wav_file_path)

        # RMS 값 계산
        rms = librosa.feature.rms(y=y)[0]

        # RMS 평균의 1.5배를 임계치로 설정
        threshold = np.mean(rms) * 1.5

        # 임계치를 처음 초과하는 샘플 인덱스 찾기
        start_sample = np.argmax(rms > threshold) * 512  # RMS는 512 프레임 간격으로 계산됨

        # 음성을 임계치 이전 신호를 잘라내기
        y_trimmed = y[start_sample:]

        sf.write(self.drum_wav_file_path, y_trimmed, sr)

    def cut_wav_to_sixteenth_notes(self):
        self.chunk_length_ms = int((60000 / self.bpm) / 4)

        self.chunked_file_path = "chunked_music/"

        if not os.path.exists(self.chunked_file_path):
            os.makedirs(self.chunked_file_path)

        # 오디오 파일 로드
        audio = AudioSegment.from_wav(self.drum_wav_file_path)

        # 파일 이름 및 확장자 분리
        base_name = os.path.splitext(os.path.basename(self.drum_wav_file_path))[0]

        # 오디오 파일 길이
        audio_length_ms = len(audio)

        # 파일을 나눠서 저장
        for i in range(0, audio_length_ms, self.chunk_length_ms):
            chunk = audio[i:i+self.chunk_length_ms]
            chunk_number = str(i // self.chunk_length_ms).zfill(4)
            chunk_name = f"{base_name}_chunk{chunk_number}.wav"
            chunk_path = os.path.join(self.chunked_file_path, chunk_name)
            chunk.export(chunk_path, format="wav")

    def predict(self):
        model = EfficientNetModel(num_classes=8)
        try:
            model.load_state_dict(torch.load('best_model.pth', map_location=torch.device('cpu')))
        except Exception as e:
            print(f"Error loading model state dict: {e}")
            import traceback
            traceback.print_exc()
        model = model.to(torch.device('cpu'))
        model.eval()  # 평가 모드로 전환

        files = os.listdir(self.chunked_file_path)

        # Transform to resize the input to 256x256
        resize_transform = transforms.Resize((256, 256))  # resize to 256x256

        for file in files:
            if file.endswith('.wav'):
                path = os.path.join(self.chunked_file_path, file)

                audio, sr = librosa.load(path, sr=None)
                stft = librosa.stft(audio, n_fft=2048, hop_length=512)
                stft_magnitude, _ = librosa.magphase(stft)
                spectrogram_db = librosa.amplitude_to_db(stft_magnitude, ref=np.max)

                # Add channel dimension and convert to tensor
                spectrogram_db = np.expand_dims(spectrogram_db, axis=0)
                spectrogram_db = torch.tensor(spectrogram_db, dtype=torch.float32)

                # Apply the resize transform
                spectrogram_db = F.interpolate(spectrogram_db.unsqueeze(0), size=(256, 256), mode='bilinear', align_corners=False)
                spectrogram_db = spectrogram_db.squeeze(0)

                # Add batch dimension and move to CPU
                spectrogram_db = spectrogram_db.unsqueeze(0).to(torch.device('cpu'))

                with torch.no_grad():
                    output = model(spectrogram_db)
                    binary_prediction = (output > 0.5).int().cpu().numpy()

                self.predictions.append(binary_prediction.tolist())

    def remove_non_ascii(self):
        self.title =  ''.join(filter(lambda x: ord(x) < 128, self.title))
        self.title = self.title.strip()

    def make_pdf(self):

        drum_lilypond_code = r'''
    \version "2.22.1"
    \header {
      title = "''' + self.title + r'''"
    }

    \layout {
      \context {
        \DrumVoice
        \omit Rest
      }
    }

    '''

        up = []
        down = []

        index_drum_dict = {
            0: "crashcymbal16",
            1: "cymr16",
            2: "snare16",
            3: "tommh16",
            4: "tomml16",
            5: "toml16",
            6: "bd16",
            7: "cb16"
        }

        # self.predictions의 예측 결과를 기반으로 악보에 음표 추가
        for prediction in self.predictions:
            prediction  = prediction[0]  # 3중 리스트에서 2중 리스트로 변환
            if prediction[6] == 1:
                down.append(index_drum_dict[6])
            else:
                down.append("r16")

            up_sum = sum(prediction[0:6]) + prediction[7]

            if up_sum == 0:
                up.append("r16")
            elif up_sum == 1:
                for i in range(0,8):
                    if i == 6:
                        continue
                    if prediction[i] == 1:
                        up.append(index_drum_dict[i])
            else:
                overlap_text = "<"
                for i in range(0,8):
                    if i == 6:
                        continue
                    if prediction[i] == 1:
                        overlap_text += index_drum_dict[i][:-2]
                        overlap_text += " "

                overlap_text = overlap_text[:-1]
                overlap_text += ">16"
                up.append(overlap_text)

        drum_lilypond_code += f'''
    up = \drummode {{
      {" ".join(up)}
    }}

    down = \drummode {{
      {" ".join(down)}
    }}

    '''

        # LilyPond 코드의 끝 부분 설정
        drum_lilypond_code += r'''

    \score {
      \new DrumStaff <<
        \new DrumVoice = "up" {
          \voiceOne
          \tempo 4 = ''' + str(round(self.bpm)) + r'''
          \up
        }
        \new DrumVoice = "down" { \voiceTwo \down }
      >>
    }
    '''

        print(drum_lilypond_code)

        # LilyPond 파일로 저장
        lilypond_filename = "drum_pattern.ly"
        with open(lilypond_filename, "w") as file:
            file.write(drum_lilypond_code)

        # PDF로 변환
        os.system(f"lilypond {lilypond_filename}")

        # 변환된 PDF 파일 이름을 출력
        pdf_filename = lilypond_filename.replace(".ly", ".pdf")

    def delete_temp_files(self):
        # 삭제할 폴더 목록
        folders_to_delete = ['chunked_music', 'music', 'pretrained_models']

        # 삭제할 파일 목록
        files_to_delete = ['drum_pattern.ly', 'music.mp3']

        # 현재 작업 경로
        current_path = os.getcwd()

        # 폴더와 그 안의 모든 파일 및 폴더 삭제
        for folder in folders_to_delete:
            folder_path = os.path.join(current_path, folder)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print(f"Deleted folder and its contents: {folder_path}")
            else:
                print(f"Folder not found: {folder_path}")

        # 개별 파일 삭제
        for file in files_to_delete:
            file_path = os.path.join(current_path, file)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                print(f"File not found: {file_path}")

    def main(self): # 모든 실행을 관리
        try:
            # 1. 받은 파일들을 처리하여 self.mp3_file에 저장한다
            if self.youtube_link is not None:
                self.save_youtube_link_to_mp3()
            elif self.mp3_file is not None:
                self.save_mp3_file()
            else:
                print("파일이 둘다 None으로 입력 됨") # 오류 처리
                return None

            # 2. bpm을 추출한다
            self.extract_bpm()

            # 3. mp3 파일에서 드럼 소리만 추출하여 drum.wav로 변환한다
            self.transform_wav_to_drum()

            # 4. 임계값 처리를 통해 드럼이 없는 전주 부분은 자른다
            self.cut_drum_intro()

            # 5. bpm 정보를 활용하여 16분음표 길이를 계산한 후, wav를 16분 음표 길이로 모두 자른다
            self.cut_wav_to_sixteenth_notes()

            # 6. 잘린 파일들을 모두 STFT 변환 시킨 후, 256*256으로 resize 시키고 model에 넣어 예측값을 뽑아낸다
            self.predict()

            # 7. 예측 결과를 토대로 악보를 그린 후 pdf를 저장한다
            self.remove_non_ascii()
            self.make_pdf()

            # 8. 채보 과정 중에 생성된 temp 파일들은 삭제한다
            self.delete_temp_files()

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        return None