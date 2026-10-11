# simulator.py
from grid_game import GridHuntGame
from agent import ModelBasedAgent, SimpleReflexAgent

def run_grid_hunt():
    env = GridHuntGame()
    agent = SimpleReflexAgent()

    print("=== IT3012 Grid Hunt Started ===")
    while not env.is_done():
        percept = env.get_percept(agent)
        action = agent.sense_and_act(percept)
        env.execute_action(agent, action)
        print(f"Pos: {percept['agent_pos']} | Food Left: {percept['remaining_food']} | Score: {percept['score']}")

    print(f"\nGame Over! Final Score: {env.score} after {env.steps} steps.")

if __name__ == "__main__":
    run_grid_hunt()