class KnowledgeBase:
    """
    Part 1: The Logic Engine Architecture
    A declarative Knowledge Base that stores Facts (current percepts)
    and Rules (Horn Clauses), and can run Forward Chaining inference
    over them.
    """

    def __init__(self):
        # Attributes
        self.facts = set()   # unique string facts, e.g. "TargetVisible"
        self.rules = []      # list of (premise_list, conclusion_string) tuples

    # ------------------------------------------------------------------
    # Step 1.1: Building the Knowledge Base
    # ------------------------------------------------------------------

    def tell_fact(self, fact_string):
        """Add a single fact to the knowledge base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        """Add a Horn Clause rule: premise_list -> conclusion_string."""
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        """Empty the facts set (used before evaluating a new tile/state)."""
        self.facts.clear()

    # ------------------------------------------------------------------
    # Step 2.1: The Inference Algorithm (Data-Driven Forward Chaining)
    # ------------------------------------------------------------------

    def forward_chain(self):
        """
        Repeatedly scans all rules and applies Modus Ponens:
        if every premise of a rule is already known, add its
        conclusion to the facts. Keeps looping until a full pass
        adds no new facts.
        """
        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                if conclusion not in self.facts:

                    # Modus Ponens Check
                    if all(premise in self.facts for premise in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True