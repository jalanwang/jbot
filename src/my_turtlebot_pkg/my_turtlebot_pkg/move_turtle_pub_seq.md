```mermaid
sequenceDiagram
    participant User
    participant MoveTurtle as Node (MoveTurtle)
    participant ROS_Master as ROS 2 MiddleWare
    participant Robot as TurtleBot (/cmd_vel)

    User->>MoveTurtle: 키보드 입력 ('w', 'a' 등)
    Note over MoveTurtle: 속도(velocity/angular) 변수 업데이트
    MoveTurtle->>MoveTurtle: Twist 메시지 생성
    MoveTurtle->>ROS_Master: msg 발행 (Publish)
    ROS_Master-->>Robot: /cmd_vel 전달
    MoveTurtle->>MoveTurtle: get_logger().info() 출력
