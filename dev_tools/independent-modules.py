import shutil
import sys
from subprocess import run

from pathlib import Path
import re
from typing import Iterable

SRC_DIR = Path(__file__).parent / '..'


def check_mod(modname: str, other_modules: Iterable[str]):
    def mrun(*args, **kwargs):
        return run(*args, check=True, env={}, **kwargs)

    work_dir = SRC_DIR / f'dev_tools/mod_envs/{modname}'

    print(f'Cloning repository for {modname}')
    src_dir = work_dir / 'repo'
    shutil.rmtree(src_dir, ignore_errors=True)
    mrun(['git', 'clone', SRC_DIR, src_dir])
    for omod in other_modules:
        to_rm = src_dir / 'recirq' / omod
        print(f'.. removing {to_rm}')
        shutil.rmtree(to_rm)

    print(f'Creating venv for {modname}')
    venv_dir = work_dir / 'venv'
    python = f'{sys.prefix}/bin/python'
    mrun([python, '-m', 'venv', '--clear', venv_dir])

    pip = [venv_dir / 'bin/pip']
    extra_reqs_fn = src_dir / 'recirq' / modname / 'extra-requirements.txt'
    if extra_reqs_fn.exists():
        extra_reqs_args = ['-r', extra_reqs_fn]
    else:
        extra_reqs_args = []

    print(f'Installing requirements for {modname}')
    cirq = ['cirq-core==1.0.0', 'cirq-google==1.0.0']
    mrun(pip + ['install'] + cirq)
    print('--')
    mrun(pip + ['install', '-r', src_dir / 'requirements.txt'] + extra_reqs_args)

    print(f'Installing test utilities for {modname}')
    mrun(pip + ['install', 'pytest'])

    print(f'Running pytest for {modname}')
    pytest = venv_dir / 'bin/pytest'
    mrun([pytest, src_dir / 'recirq', '-v'])


NOT_INDEPENDENT = ['optimize', 'algo_benchmarks']


def main():
    o = run(['git', 'ls-files', 'recirq/*/__init__.py'], capture_output=True,
            universal_newlines=True, cwd=SRC_DIR)

    glob_fns = o.stdout.splitlines()
    mods = []
    for fn in glob_fns:
        if ma := re.match(r'recirq/(\w+)/__init__\.py', fn):
            mod = ma.group(1)

            if mod in NOT_INDEPENDENT:
                continue

            mods.append(mod)
    print(mods)
    submods = set(glob_fns) - set(f'recirq/{mod}/__init__.py' for mod in mods)
    for x in submods:
        print(x)

    for mod in mods:
        if mod == 'quantum_chess':
            # shim
            continue

        other_mods = set(mods)
        other_mods.remove(mod)
        check_mod(mod, other_modules=other_mods)


if __name__ == '__main__':
    main()
