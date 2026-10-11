from logic_engine import KnowledgeBase


def test_forward_chaining():
    kb = KnowledgeBase()
    kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
    kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    kb.tell_fact('HasDust')
    kb.forward_chain()
    assert 'SafeToEngage' in kb.facts, 'Should deduce SafeToEngage'
    assert 'Retreat' not in kb.facts, 'Should not deduce Retreat'

    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    kb.tell_fact('HasDust')
    kb.tell_fact('BloodseekerMissing')
    kb.forward_chain()
    assert 'Retreat' in kb.facts, 'Should deduce Retreat'


if __name__ == '__main__':
    test_forward_chaining()
    print('All Logic Engine Test Cases Passed!')