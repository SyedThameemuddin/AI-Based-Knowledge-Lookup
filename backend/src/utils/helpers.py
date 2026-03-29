class KnowledgeHelper:
    """
    Simple helper class for error logging.
    (Replaces CoffeeShopHelper — DB dependency removed, uses console logging only.)
    """

    def __init__(self):
        pass

    def error_logger(self, function_name: str, file_name: str, error: str):
        """Log error details to console (no DB required)."""
        try:
            print("\n" + "=" * 50)
            print(f"❌ ERROR in: {function_name}")
            print(f"   File   : {file_name}")
            print(f"   Detail : {error}")
            print("=" * 50 + "\n")
        except Exception as e:
            print(f"\nFailed to log error: {str(e)}")