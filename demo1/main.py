from pathlib import Path
from flow import run_flow

if __name__ == '__main__':
    base = Path(__file__).resolve().parent
    summary = run_flow(str(base))
    print('First demo summary:')
    for k, v in summary.items():
        print(f'- {k}: {v}')

        