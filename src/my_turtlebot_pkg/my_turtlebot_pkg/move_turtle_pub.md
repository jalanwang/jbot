```mermaid
classDiagram
    class Node {
        <<ROS 2 Library>>
        +create_publisher()
        +create_timer()
        +get_logger()
        +destroy_node()
    }

    class MoveTurtle {
        +qos_profile: QoSProfile
        +move_turtle: Publisher
        +velocity: float
        +angular: float
        +__init__()
        +turtle_move()
        +turtle_key_move()
    }

    class Twist {
        <<ROS 2 Message>>
        +linear: Vector3
        +angular: Vector3
    }

    Node <|-- MoveTurtle : Inheritance
    MoveTurtle ..> Twist : Depends on (Publish)
    MoveTurtle --> "1" QoSProfile : Uses
