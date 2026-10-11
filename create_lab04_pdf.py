"""Create a self-contained PDF submission from Lab_04_Answers.md content.

This uses only the Python standard library so the completed lab document can be
regenerated without installing a PDF package.
"""

from pathlib import Path
import textwrap


OUTPUT = Path('IT24101673_SE3062_Practical_04.pdf')
PAGE_WIDTH, PAGE_HEIGHT = 595, 842  # A4 in PDF points
LEFT, TOP, BOTTOM = 54, 790, 52
LINE_HEIGHT = 15

SECTIONS = [
    ('IT3012: Intelligent Agents - Practical 04', [
        'Informed Search - Completed Submission',
        '',
        'Part 1: Implementation completed',
        '- Added manhattan_distance(pos, goal) and euclidean_distance(pos, goal) to SearchAgent.',
        "- Added astar_search(..., heuristic_type='manhattan') using a heapq priority queue ordered as",
        '  (f_cost, g_cost, current_pos, path_taken).',
        '- Added AStar to sense_and_act and set the visual game to use AStar by default.',
        '- Step 1.1 checkpoint: Manhattan((0, 0), (3, 4)) = 7; Euclidean = 5.0.',
    ]),
    ('1. UCS and A* priority', [
        'UCS prioritizes the frontier node with the smallest path cost already incurred, g(n).',
        'A* prioritizes the smallest estimated total path cost, f(n) = g(n) + h(n). Therefore',
        'A* also uses a heuristic estimate of the remaining cost to guide the search toward the goal.',
    ]),
    ('2. Why Manhattan distance is admissible for this grid', [
        'In a four-way grid, each legal move changes either x or y by one and costs one step. The',
        'agent must make at least |x1-x2| + |y1-y2| moves to reach the goal; walls only make a',
        'route longer. Manhattan distance never overestimates the remaining cost, so it is admissible.',
        'If a heuristic is not admissible, A* may choose a suboptimal path and loses its optimality guarantee.',
    ]),
    ('3. Eight-way movement', [
        'No, not when diagonal moves cost one. From (0, 0) to (3, 3), Manhattan distance is 6,',
        'but the goal can be reached in three diagonal moves, so Manhattan overestimates. Use',
        'Chebyshev distance, max(|dx|, |dy|), for unit-cost eight-way movement. If diagonal moves',
        'cost sqrt(2), use octile distance (Euclidean distance is also an admissible lower bound).',
    ]),
    ('4. Stronger heuristic for all remaining food', [
        'Use the distance from the current position to the nearest remaining food plus the cost of a',
        'minimum spanning tree (MST) over all remaining food locations. Use maze shortest-path',
        'distances (precomputed with BFS) as edge weights so walls are considered. Every complete',
        'route must first reach a pellet and connect all others, making this an admissible and stronger',
        'lower bound than the distance to only the closest food item.',
    ]),
]


def escape_pdf(text):
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def build_pages():
    pages, lines = [], []
    capacity = (TOP - BOTTOM) // LINE_HEIGHT

    def add(line, size=10, bold=False):
        nonlocal lines
        if len(lines) >= capacity:
            pages.append(lines)
            lines = []
        lines.append((line, size, bold))

    for title, paragraphs in SECTIONS:
        if lines:
            add('')
        add(title, 14 if title.startswith('IT3012') else 12, True)
        for paragraph in paragraphs:
            if not paragraph:
                add('')
                continue
            for line in textwrap.wrap(paragraph, width=94, break_long_words=False):
                add(line)
    if lines:
        pages.append(lines)
    return pages


def page_stream(lines):
    commands = ['BT']
    y = TOP
    for line, size, bold in lines:
        font = 'F2' if bold else 'F1'
        commands += [f'/{font} {size} Tf', f'1 0 0 1 {LEFT} {y} Tm', f'({escape_pdf(line)}) Tj']
        y -= LINE_HEIGHT + (3 if bold else 0)
    commands.append('ET')
    return '\n'.join(commands).encode('latin-1')


def make_pdf():
    pages = build_pages()
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        None,
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>',
    ]
    page_refs = []
    for lines in pages:
        page_number = len(objects) + 1
        content_number = page_number + 1
        page_refs.append(page_number)
        stream = page_stream(lines)
        objects.extend([
            (f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] '
             f'/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_number} 0 R >>').encode(),
            b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream',
        ])
    objects[1] = ('<< /Type /Pages /Kids [' + ' '.join(f'{ref} 0 R' for ref in page_refs) +
                  f'] /Count {len(page_refs)} >>').encode()

    pdf = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(pdf)
    pdf.extend(f'xref\n0 {len(objects) + 1}\n0000000000 65535 f \n'.encode())
    pdf.extend(b''.join(f'{offset:010d} 00000 n \n'.encode() for offset in offsets[1:]))
    pdf.extend(f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    OUTPUT.write_bytes(pdf)


if __name__ == '__main__':
    make_pdf()
    print(f'Created {OUTPUT.resolve()}')
