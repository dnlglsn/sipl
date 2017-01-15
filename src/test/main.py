import unittest
import coverage
import StringIO

# References:
# http://docs.python.org/2/library/unittest.html
# http://nedbatchelder.com/code/coverage/
# http://docs.python.org/2/library/stringio.html
# http://stackoverflow.com/questions/2266646/how-to-i-disable-and-re-enable-console-logging-in-python

if __name__ == "__main__":

    # Create a new coverage object
    omittedFiles = ["*main.py", "*__init__*"]
    cov = coverage.coverage(source=["sipl"], omit=omittedFiles)

    # Start the code coverage before discovering the modules
    cov.start()

    # Go through the folder and find all the files ending in "_test.py"
    loader = unittest.TestLoader()
    tests = loader.discover(start_dir=".", pattern="*_test.py")

    # Setup the runner showing the entire testing progress
    testRunner = unittest.runner.TextTestRunner(verbosity=2)

    print ""
    print "=============="
    print "= UNIT TESTS ="
    print "=============="
    print ""

    # Run the tests
    testRunner.run(tests)

    # Stop the code coverage
    cov.stop()

    print ""
    print "================="
    print "= CODE COVERAGE ="
    print "================="
    print ""

    # Use a fake file object so I can print the coverage report out to console
    reportFile = StringIO.StringIO()

    # Write the coerage report
    cov.report(file=reportFile)

    # Print out the contents
    print reportFile.getvalue()
