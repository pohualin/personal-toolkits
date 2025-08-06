class Utils:
    @staticmethod
    def is_empty(s):
        """Return True if the string is None or empty."""
        return not s or s.strip() == ""

    @staticmethod
    def to_upper(s):
        """Convert a string to uppercase."""
        return s.upper() if s else s

    @staticmethod
    def join_list(lst, sep=","):
        """Join a list of strings with a separator."""
        return sep.join(lst)

# Example usage:
if __name__ == "__main__":
    print(Utils.is_empty("   "))         # True
    print(Utils.to_upper("hello"))       # HELLO
    print(Utils.join_list(["a", "b"]))   # a,b