from agent import SimpleReflexAgent, ModelBasedAgent, SearchAgent
from grid_game import GridHuntGame


def run_agent(agent, name, seed=7):
    env = GridHuntGame(seed=seed)

    print(f"=== {name} ===")

    while not env.is_done():
        # Only the local percept is passed to the agent.
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)

        print(
            f"Step {env.steps:02d}: "
            f"percept={percept} action={action:<7} "
            f"score={env.score} food_left={len(env.food_positions)}"
        )

    print(
        f"Final score: {env.score}; "
        f"steps: {env.steps}; "
        f"food left: {len(env.food_positions)}\n"
    )


def demonstrate_memory():
    """Demonstrate that repeated percepts can produce different actions."""
    agent = ModelBasedAgent()
    percept = {'wall_ahead': True, 'food_here': False}

    first = agent.sense_and_act(percept)
    second = agent.sense_and_act(percept)

    print("=== Model-Based Memory Demonstration ===")
    print(f"Same percept #1 -> {first}")
    print(f"Same percept #2 -> {second}")
    print(f"Different actions: {first != second}\n")


if __name__ == '__main__':
    run_agent(SimpleReflexAgent(), 'Simple Reflex Agent')
    run_agent(ModelBasedAgent(), 'Model-Based Agent')
    demonstrate_memory()


def run_search_agent(algorithm='AStar', seed=7):
    """Run the SearchAgent with the selected search algorithm."""
    env = GridHuntGame(seed=seed)
    agent = SearchAgent()
    agent.active_algo = algorithm

    while not env.is_done():
        percept = {
            'grid_size': (env.width, env.height),
            'walls': list(env.walls),
            'all_food': list(env.food_positions),
        }
        action = agent.sense_and_act(percept)
        env.execute_action(action)

    print(
        f"=== SearchAgent ({algorithm}) ===\n"
        f"Final score: {env.score}; steps: {env.steps}; "
        f"food left: {len(env.food_positions)}"
    )


if __name__ == '__main__':
    run_search_agent('AStar')
