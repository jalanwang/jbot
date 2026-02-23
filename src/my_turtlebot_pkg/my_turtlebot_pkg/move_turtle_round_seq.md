```mermaid
sequenceDiagram
    participant OS as Main Process
    participant Node as Move_turtle Node
    participant Timer as Timer Event (1Hz)
    participant Topic as /turtle1/cmd_vel


    OS->>Node: rclpy.init() & Node 생성
    Node->>Node: velocity = -1.0 초기화
    loop rclpy.spin(node)
        Timer->>Node: turtle_move() 콜백 호출
        Node->>Node: Twist 메시지 생성 (linear.x = velocity)
        Node->>Topic: publish(msg)
        Note right of Node: velocity += 0.08 증가
        alt velocity > 2.0
            Node->>Node: velocity = 0.0 리셋
        end
    end
    OS->>Node: Ctrl+C (KeyboardInterrupt)
    Node->>OS: rclpy.shutdown()
