# This is a Python 3.5 specific formula.
include:
    - python.python35
    - python.pip

pylint:
    pip.installed:
        - name: pylint==1.5.4
        - bin_env: /usr/local/bin/pip3
        - require:
            - sls: python.python35
            - sls: python.pip
