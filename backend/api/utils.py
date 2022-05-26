from core.exceptions import InvalidShoppingListDataError


def generate_shopping_list(ingredients: list, username: str) -> list:
    """Create shopping list for given user."""
    try:
        shopping_list = [
            (
                f'FOODGRAM список покупок '
                f'для пользователя {username}\n\n'
            )
        ]
        for i, item in enumerate(ingredients, start=1):
            shopping_list.append(
                (
                    f'{i}. '
                    f'{item["ingredient__name"]} '
                    f'({item["ingredient__measurement_unit"]}) - '
                    f'{item["amount_sum"]}\n'
                )
            )
        return shopping_list
    except Exception as e:
        raise InvalidShoppingListDataError(e)
