"""A small propositional-logic knowledge base with forward chaining."""


class KnowledgeBase:
    """Store string facts and Horn-clause rules, and infer conclusions."""

    def __init__(self):
        self.facts = set()
        self.rules = []

    def tell_fact(self, fact_string):
        """Add a fact to the knowledge base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        """Append a rule as (premises, conclusion)."""
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        """Remove all facts while retaining the rules."""
        self.facts.clear()

    def forward_chain(self):
        """Apply rules repeatedly until a full pass adds no new facts."""
        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                if conclusion not in self.facts and all(
                    premise in self.facts for premise in premises
                ):
                    self.facts.add(conclusion)
                    new_facts_added = True
