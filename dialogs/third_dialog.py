# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult, ComponentDialog
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.core import MessageFactory
from datatypes_date_time.timex import Timex

from .cancel_and_helping import CancelAndHelpDialog


class ThirdDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(self, dialog_id: str = None):
        super(ThirdDialog, self).__init__(dialog_id or ThirdDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        # self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                    self.origin_step,
                    self.travel_date_step,
                    self.confirm_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for destination."""
        booking_details = step_context.options

        if booking_details.destination is None:
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(
                    prompt=MessageFactory.text("Это второй диалог и первый вопрос?")),)
        else:
            return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Это второй диалог и второй вопрос?")),)
        else:
            return await step_context.next(booking_details.origin)

    async def travel_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.origin = step_context.result
        if not booking_details.travel_date or self.is_ambiguous(booking_details.travel_date):
            return await step_context.next(booking_details.travel_date)

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.travel_date = step_context.result
        msg = (
            f"Всё правильно? Состояние первого вопросы: { booking_details.destination }"
            f" и второго: { booking_details.origin }."
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        if step_context.result:
            booking_details = step_context.options
            booking_details.travel_date = step_context.result

            return await step_context.end_dialog(booking_details)
        else:
            return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
