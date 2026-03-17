#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 설정 변수
SAVE_DIR="${SCRIPT_DIR}/datasets/captures/images"
INTERVAL=3.0
HZ=$(echo "scale=3; 1/$INTERVAL" | bc) # 0.333Hz
INPUT_TOPIC="/camera/image_raw"
THROTTLED_TOPIC="/camera/image_throttled"

# 저장 폴더 생성
mkdir -p "$SAVE_DIR"

echo "[INFO] 3초 간격 자동 저장을 시작합니다."

# 1. Throttle 실행 (백그라운드)
# 3초당 1장만 가도록 토픽 속도 조절
ros2 run topic_tools throttle messages $INPUT_TOPIC $HZ $THROTTLED_TOPIC &
THROTTLE_PID=$!

# 종료 시 백그라운드 프로세스 정리
trap "kill $THROTTLE_PID; exit" SIGINT SIGTERM

# 2. Image Saver 실행 (포어그라운드)
# 동기화 경고를 무시하고 들어오는 모든 이미지를 저장
ros2 run image_view image_saver --ros-args \
  -p save_all_images:=true \
  -p filename_format:="${SAVE_DIR}/img_%04d.jpg" \
  --remap image:=$THROTTLED_TOPIC \
  --param _approximate_sync:=true

kill $THROTTLE_PID
