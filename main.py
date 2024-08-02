from src.api.hh_api import HHAPI
from src.utils import setup_logger
from src.models.interaction import SearchInteraction, UserInteraction

logger = setup_logger(__name__)

def main():
    api = HHAPI()
    storage = None

    while True:

        print("1. Поиск вакансий")
        print("2. Работа с вакансиями")
        print("3. Выйти")
        
        choice = input("Выберите опцию: ")


        
        if choice == "1":

            logger.info("Выполняется поиск вакансий.")


            search_interaction = SearchInteraction(api)
            storage = search_interaction.interact()
            
            print("\nПоиск завершен.")

            print(f"Найдено {len(storage)} вакансий.\n")
            logger.info(f"Найдено {len(storage)} вакансий.")

            input("Для продолжения нажмите Enter\n")

            if storage == 0:
                logger.info("Вакансий не найдено.")
                continue
            
            user_interaction = UserInteraction(storage)
            user_interaction.interact()


        elif choice == "2":
            logger.info("Выполняется работа с вакансиями.")
            if not storage:
                logger.info("Вакансий не найдено.")
                print("\nСначала выполните поиск вакансий.")
                input("Для продолжения нажмите Enter\n")
                continue
            user_interaction = UserInteraction(storage)
            user_interaction.interact()

            logger.info("Работа с вакансиями завершена.")
        
        elif choice == "3":
            break
        
        else:
            logger.info("Неверный выбор пользователя")
            print("Неверный выбор, попробуйте еще раз.")

if __name__ == "__main__":
    logger.info("Программа запущена")
    main()
