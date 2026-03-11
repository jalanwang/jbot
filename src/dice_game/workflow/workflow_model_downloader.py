from roboflow import Roboflow

# 1. 로그인 및 프로젝트 접속
rf = Roboflow(api_key="vPiSncB9kqdHaS9JuOgD") # Settings -> General에 있음
project = rf.workspace().project("finddice") # 네 프로젝트 ID
version = project.version(2) # 네가 확인한 버전 번호

# 2. 모델 가중치(.pt) 다운로드
# 이 명령어를 실행하면 현재 폴더에 'weights' 폴더가 생기고 그 안에 best.pt가 저장돼.
version.model.download("pt")