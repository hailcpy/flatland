# create randomized versions of a single program,
# provided as string input
import json
import os
import random

import flatland.utils.config as CONFIG
from flatland.lang.run import run_mul as runner
from flatland.utils.modding import finalize
from flatland.utils.modding import initialize
from flatland.utils.randomizer import GENERATE_FILEID


def main(programs: list, filename: str, num_samples: int, outdir: str, num_sub: int):
    outdir = os.path.abspath(outdir)
    CONFIG.RANDOMIZE = True
    CONFIG.RUN = True
    CONFIG.SHOWTURTLE = False
    CONFIG.SKIPIMAGE = True
    initialize()
    newpath = os.path.join(outdir, filename)
    basename = os.path.splitext(os.path.basename(filename))[0]
    for i in range(num_samples):
        newname = f"{basename}-{GENERATE_FILEID()}"
        CONFIG.SKIPIMAGE = True
        expr, info = runner(random.sample(programs, num_sub), filename, env=None)

        newpath = os.path.join(outdir, newname)
        with open(newpath + ".lisp", "w") as f2:
            f2.write(str(expr))

        with open(newpath + ".json", "w") as f3:
            json.dump(info, f3, indent=4)

        CONFIG.SKIPIMAGE = False
        finalize(newpath + ".lisp")


if __name__ == "__main__":
    main()
