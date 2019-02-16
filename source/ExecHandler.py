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
    """Custom class for errors when the executable returns an error."""
    pass

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
            logger.critical("cannot make holdem-eval executable")
            logger.critical("command {} failed with exit status {!s}".format(
                e.cmd, e.returncode))
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
        logger.error("cannot clean holdem-eval directory")
        logger.error("command {} failed with exit status {!s}".format(
            e.cmd,e.returncode))
        logger.error("trace of stderr: \n{}".format(e.stderr))
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

    The function takes in a list of ranges, which must be at least 2 and no
    more than 6.  If the list of arguments is invalid, an ExecError is
    returned.  An ExecRunError (child of ExecError) is returned if the
    executable returns an error.  Note that this is not returned if the
    executable runs out of time but has no other errors.  The range list is a
    list of strings, to be passed directly into the executable.

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
    pass

if __name__ == "__main__":
    #this "main method" is used for testing the utility.  not to actually be
    #used.  it is never run when the file is exported
    from RedditHandler import setup_logging
    setup_logging()
    check_exec(clean_dependencies=False) #change to True to save a bit of space
