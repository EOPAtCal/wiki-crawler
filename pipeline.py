import subprocess
import crawl
import preprocess
from utils import *


if __name__ == "__main__":
    # crawl.main()
    preprocess.main()
    if subprocess.call(['chmod', '+x', 'copy_into_server.sh']) == 0:
        print "successfully made script executable"
        print_a_line()
        if subprocess.call(['./copy_into_server.sh']) == 0:
            print "successfully copied files into the server"
            print_a_line()
            print "Pipeline completed successfully"
