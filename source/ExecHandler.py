#!/usr/bin/env python3

"""This file, written by Andrew H. Pometta, is the file responsible for
interfacing with the equity analysis executable.  It is used by the main
Python file for this program, reddit_handler.py, to go between the executable
and the rest of the program.  It also performs the text parsing, and raises
exceptions based on various errors that may occurr during parsing or in
the executable's running."""

import logging
import subprocess

HE_EXEC_FILENAME = "holdem-eval"
HE_EXEC_DIRNAME = "holdem-eval/"
HE_EXEC_PATHNAME = HE_EXEC_DIRNAME + HE_EXEC_FILENAME
MAKEFILE_PATHNAME = HE_EXEC_DIRNAME + "Makefile"

class ExecError(Exception):
    """Custom class for errors when handling the executable."""
    pass

class ExecAccessError(ExecError):
    """Custom class for errors when the executable cannot be accessed."""
    pass

class ExecRunError(ExecError):
    """Custom class for errors when the executable returns an error.

    This exception also contains the exit status of the ran executable.
    Useful for printing custom exceptions."""
    def __init__(self, message, errcode):
        super().__init__(message)
        self.errcode = errcode #error code of the executable


def check_exec(clean_dependencies=False):
    """Ensure holdem-eval executable is present in target directory.

    This function checks if the holdem-eval executable is present in the
    target directory.  If it is not, it attempts to find and use the Makefile
    included in the project to create it, and optionally clean dependencies
    afterwards.  If it cannot do this, it raises the custom exception
    ExecError.

    :param clean_dependencies: Cleans unneeded dependencies after compilation.
    Does not clean dependencies if the executable is present before running.
    """
    logger = logging.getLogger("ex_logger")
    try:
        #exit status 0 if file exists, 1 if it does not
        subprocess.run(["test", "-e", HE_EXEC_PATHNAME], check=True)
        logger.debug("holdem-eval exec found")
    except subprocess.CalledProcessError:
        #exec not found: attempt to make
        #make sure Makefile is present first
        try:
            logger.debug("holdem-eval exec not found: making")
            subprocess.run(["test", "-e", MAKEFILE_PATHNAME], check=True)
            logger.debug("Makefile found")
        except subprocess.CalledProcessError:
            logger.critical("Neither holdem-eval exec nor Makefile found")
            raise ExecAccessError("Makefile not found in expected directory")
        try:
            #Makefile found
            subprocess.run(["make", "-C", HE_EXEC_DIRNAME],
                           stderr=subprocess.PIPE, check=True)
            logger.info("holdem-eval made successfully")
            if clean_dependencies:
                subprocess.run(["make", "-C", HE_EXEC_DIRNAME,
                                "clean-dependencies"], stderr=subprocess.PIPE,
                               check=True)
                logger.info("holdem-eval dependencies cleaned")
                #sanity check
                subprocess.run(["test", "-e", HE_EXEC_PATHNAME], check=True)
        except subprocess.CalledProcessError as e:
            #any one of the 3 above commands could have failed
            logger.critical("cannot make holdem-eval executable: "
                            "command {} failed with exit status {!s}"
                            .format(e.cmd, e.returncode))
            logger.critical("trace of stderr: \n{}".format(e.stderr))
            raise ExecAccessError("failed to make executable")
    except:
        logger.critical("Unexpected error when checking executable",
                        exc_info=True)
        raise ExecError("Unexpected error when checking executable")

def clean_exec():
    """Run \"make clean\" in executable directory."""
    logger = logging.getLogger("ex_logger")
    try:
        subprocess.run(["make", "-C", HE_EXEC_DIRNAME, "clean"], check=True,
                       stderr=subprocess.PIPE)
        logger.info("executable and dependencies cleaned")
    except subprocess.CalledProcessError as e:
        logger.error("cannot clean holdem-eval directory: command {} failed "
                     "with exit status {!s}".format(e.cmd, e.returncode))
        logger.debug("trace of stderr: \n{}".format(e.stderr))
        raise ExecError("failed to clean executable directory")
    except:
        logger.error("Unexpected error when cleaning executable",
                     exc_info=True)
        raise ExecAccessError("Unexpected error when checking executable")

def run_exec(ranges, **kwargs):
    """Function for running the holdem-eval executable.

    This function is responsible for, given known arguments and options,
    running the holdem-eval executable and returning the result as a
    dictionary, containing the ranges and tuples corresponding to a string
    representing the range, the equity in the given calculation, and optionally
    the percentage of hands that that range represents.

    The function takes in a list or set of ranges of length between 2 and 6
    inclusive, in addition to keyword arguments that represent options.  If
    ranges has a different length than specified above, or is not a set or
    list, it is invalid and an ExecError is raised.  Otherwise, if the
    executable proper is run but returns an error, an ExecRunError is raised.
    An ExecRunError is NOT raised when the executable runs out of time.

    The rest of the keyword-indexed arguments serve as options to the
    executable.  They are as follows:

    :param monte_carlo: enables monte_carlo enumeration (--mc).  Note: while
    the executable has this off by default, calling this function without
    specifying this will result in it being enabled.  Set to false to disable.
    :param board: String corresponding to the board cards (-b).  Default
    empty.
    :param dead: String corresponding to the dead cards (-d).  Default empty.
    :param error: Margin of error for monte-carlo enumeration (-e).  Default
    1e-4, or 0.001%.  If monte_carlo is false, this does nothing.
    :param time: Maximum time for simulation (-t).  Note: while the default
    time of the executable is 30 seconds, this function uses 15 seconds as the
    default if not specified.

    :return The function returns a pair.  The first element is True if the
    executable completed in time and False if it did not.  The second is
    a list of pairs, corresponding to the range strings and their equities."""
    #Check immediately if the range list is of the appropriate size.
    logger = logging.getLogger("ex_logger")
    if not type(ranges) is list and not type(ranges) is set:
        logger.error("ranges not list or set")
        logger.debug("ranges: {!s}".format(ranges))
        raise ExecError("ranges not list or set")
    elif len(ranges) < 2:
        logger.error("less than 2 ranges specified")
        logger.debug("ranges: {!s}".format(ranges))
        raise ExecError("ranges too short")
    elif len(ranges) > 6:
        logger.error("more than 6 ranges specified")
        logger.debug("ranges: {!s}".format(ranges))
        raise ExecError("ranges too long")
    #make sure each range is a string
    for r in ranges:
        #note: in Python 3, all strings are unicode
        if not type(r) is str:
            logger.error("ranges contains non-string element")
            logger.debug("element in question: {!s}, ranges: {!s}"
                         .format(r, ranges))
            raise ExecError("ranges contains non-string element")
        #Check if strings are multiple words - complain if they are
        r = r.strip()
        if " " in r or "\n" in r or "\t" in r:
            logger.error("ranges contains multple-word argument \"{}\""
                         .format(r))
            raise ExecError("ranges contains multiple-word argument \"{}\""
                            .format(r))

    #check kwargs for options.  exec_call is the list for the shell command
    exec_call = [HE_EXEC_PATHNAME, "--format"]
    if "board" in kwargs:
        exec_call += ["-b", str(kwargs.pop("board"))]
    if "dead" in kwargs:
        exec_call += ["-d", str(kwargs.pop("dead"))]
    #monte_carlo is on by default in our program, but not the executable
    if not "monte_carlo" in kwargs or kwargs.pop("monte_carlo"):
        exec_call += ["--mc"]
    if "error" in kwargs:
        exec_call += ["-e", str(kwargs.pop("error"))]
    #holdem-eval default time is 30, but we want our default time to be
    #15 and overwritable
    if not "time" in kwargs:
        exec_call += ["-t", "15"]
    else:
        exec_call += ["-t", str(kwargs.pop("time"))]
    #kwargs should be empty at this point
    for key in kwargs:
        logger.warning("unrecognized option {!s} in check_exec (value: {!s})"
                       .format(key, kwargs[key]))
    exec_call += ranges #append ranges
    logger.debug("exec_call: {!s}".format(exec_call))

    #call the executable
    try:
        equity = subprocess.run(exec_call, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8") #e.stderr is bytes object by default
        error = stderr[stderr.rindex(':')+1:].strip()
        logger.error("executable failed with error code {!s} and error "
                     "message \"{!s}\"".format(e.returncode, error))
        raise ExecRunError(error, e.returncode)
    except:
        logger.error("unexpected error when calling executable", exc_info=True)

    #equity contains output from program
    output_lines = equity.stdout.decode("utf-8").splitlines()
    logger.debug("output_lines: {!s}".format(output_lines))
    success = int(output_lines[0]) == 0
    results = output_lines[1:output_lines.index("")]
    equities = []
    for range in results:
        range_str = range[:range.index(':')].strip()
        #a mouthful of a line: everything after the colon, removed of
        #whitespace and % signs, then divided by 100
        equity = float(range[range.index(':')+1:].strip().strip('%')) / 100
        equities.append((range_str, equity))

    logger.debug("{!s}".format((success, equities)))
    return success, equities

if __name__ == "__main__":
    #this "main method" is used for testing the utility.  not to actually be
    #used.  it is never run when the file is exported
    from RedditHandler import setup_logging
    setup_logging()
    logger = logging.getLogger("ex_logger")
    check_exec(clean_dependencies=True)
    ranges = ["AA", "KK QQ JJ TT 99"]
    try:
        run_exec(ranges)
    except ExecRunError as e:
        logger.debug("Message: {!s}\nReturn code: {!s}".format(e, e.errcode))
    except ExecError as e:
        logger.debug("ExecError: {!s}".format(e))
    except:
        logger.debug("Unexpected exception in run_exec", exc_info=True)
