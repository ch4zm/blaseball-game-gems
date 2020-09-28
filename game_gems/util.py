import sys
from io import StringIO

class CaptureStdout(object):
    """
    A utility object that uses a context manager
    to capture stdout.
    """
    def __init__(self):
        # Boolean: should we pass everything through to stdout?
        # (this object is only functional if passthru is False)
        super().__init__()

    def __enter__(self):
        """
        Open a new context with this CaptureStdout
        object. This happens when we say
        "with CaptureStdout() as output:"
        """
        # We want to swap out sys.stdout with
        # a StringIO object that will save stdout.
        # 
        # Save the existing stdout object so we can
        # restore it when we're done
        self._stdout = sys.stdout
        # Now swap out stdout 
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        """
        Close the context and clean up.
        The *args are needed in case there is an
        exception (we don't deal with those here).
        """
        # Store the result we got
        self.value = self._stringio.getvalue()

        # Clean up (if this is missing, the garbage collector
        # will eventually take care of this...)
        del self._stringio

        # Clean up by setting sys.stdout back to what
        # it was before we opened up this context.
        sys.stdout = self._stdout

    def __repr__(self):
        """When this context manager is printed, it looks like the game ID string"""
        return self.value
