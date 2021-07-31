import receipt_class
import typing
import calendar
import datetime

from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery



def start(
    name: str = "receipt",
    ) -> InlineKeyboardMarkup:

    receipt_callback = CallbackData("receipt_1", "action")
    data_new_receipt = receipt_callback.new("NEW_RECEIPT")
    data_show_receipts = receipt_callback.new("SHOW_RECEIPTS")
    data_other = receipt_callback.new("OTHER")

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            "Neue Quittung abgeben",
            callback_data=data_new_receipt,
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            "Meine Quittungen ansehen",
            callback_data=data_show_receipts,
        )
    )
    #keyboard.add(
    #    InlineKeyboardButton(
    #        "Quittung bearbeiten",
    #        callback_data=data_other,
    #    )
    #)

    return keyboard

def get_cause(
    name: str = "receipt",
    ) -> InlineKeyboardMarkup:

    receipt_callback = CallbackData("receipt_1", "action")
    data_sola21 = receipt_callback.new("SOLA21")
    data_other_cause = receipt_callback.new("OTHER")

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            "Sola 21",
            callback_data=data_sola21,
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            "Anderer",
            callback_data=data_other_cause,
        )
    )

    return keyboard


def do_nothing():
    return 0



class CallbackData:
    """
    Callback data factory
    """

    def __init__(self, prefix, *parts, sep=":"):
        if not isinstance(prefix, str):
            raise TypeError(
                f"Prefix must be instance of str not {type(prefix).__name__}"
            )
        if not prefix:
            raise ValueError("Prefix can't be empty")
        if sep in prefix:
            raise ValueError(f"Separator {sep!r} can't be used in prefix")
        if not parts:
            raise TypeError("Parts were not passed!")

        self.prefix = prefix
        self.sep = sep

        self._part_names = parts

    def new(self, *args, **kwargs) -> str:
        """
        Generate callback data

        :param args:
        :param kwargs:
        :return:
        """

        args = list(args)

        data = [self.prefix]

        for part in self._part_names:
            value = kwargs.pop(part, None)
            if value is None:
                if args:
                    value = args.pop(0)
                else:
                    raise ValueError(f"Value for {part!r} was not passed!")

            if value is not None and not isinstance(value, str):
                value = str(value)

            if not value:
                raise ValueError(f"Value for part {part!r} can't be empty!'")
            if self.sep in value:
                raise ValueError(
                    f"Symbol {self.sep!r} is defined as the separator and can't be used in parts' values"
                )

            data.append(value)

        if args or kwargs:
            raise TypeError("Too many arguments were passed!")

        callback_data = self.sep.join(data)
        if len(callback_data) > 64:
            raise ValueError("Resulted callback data is too long!")

        return callback_data

    def parse(self, callback_data: str) -> typing.Dict[str, str]:
        """
        Parse data from the callback data

        :param callback_data:
        :return:
        """

        prefix, *parts = callback_data.split(self.sep)

        if prefix != self.prefix:
            raise ValueError("Passed callback data can't be parsed with that prefix.")
        elif len(parts) != len(self._part_names):
            raise ValueError("Invalid parts count!")

        result = {"@": prefix}
        result.update(zip(self._part_names, parts))

        return result

    def filter(self, **config):
        """
        Generate filter

        :param config:
        :return:
        """

        print(config, self._part_names)
        for key in config.keys():
            if key not in self._part_names:
                return False

        return True

