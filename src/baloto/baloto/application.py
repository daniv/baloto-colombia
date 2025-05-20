class Application:
    def __init__(self): ...

    def run(self) -> int: ...


def main() -> int:
    exit_code: int = Application().run()
    return exit_code


if __name__ == "__main__":
    main()
