from block1 import main as run_block1
from block2 import main as run_block2
from block3 import main as run_block3
from block4 import main as run_block4


def main():
    # Запускаємо всі блоки по черзі.
    run_block1()
    print()
    run_block2()
    print()
    run_block3()
    print()
    run_block4()


if __name__ == "__main__":
    main()
