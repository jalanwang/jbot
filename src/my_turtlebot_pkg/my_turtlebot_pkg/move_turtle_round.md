```mermaid
classDiagram
    direction BT
    class Node {
        <<Library: rclpy>>
        +create_publisher()
        +create_timer()
        +destroy_node()
    }
    class Move_turtle {
        +qos_profile: QoSProfile
        +move_turtle: Publisher
        +timer: Timer
        +velocity: float
        +__init__()
        +turtle_move()
    }
    class Publisher {
        <<Library: rclpy>>
        +publish(msg)
    }
    class Timer {
        <<Library: rclpy>>
    }
    class Twist {
        <<Message: geometry_msgs>>
        +linear: Vector3
        +angular: Vector3
    }

    Move_turtle --|> Node : 상속 (Is-a)
    Move_turtle o-- Publisher : 구성 (Has-a)
    Move_turtle o-- Timer : 구성 (Has-a)
    Move_turtle ..> Twist : 의존 (Uses)
