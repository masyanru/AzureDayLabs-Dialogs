# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

import json
import os
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult, ComponentDialog, DialogTurnStatus
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.core import MessageFactory, CardFactory
from datatypes_date_time.timex import Timex
from botbuilder.schema import Activity, Attachment
from helpers.activity_helper import create_activity_reply

from .cancel_and_helping import CancelAndHelpDialog


class CardDialog(ComponentDialog):
    """Flight booking implementation."""

    def __init__(self, dialog_id: str = None):
        super(CardDialog, self).__init__(dialog_id or CardDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                                        [
                                            self.first_step,
                                            self.confirm_step,


                                        ],
                                        )
                        )
        self.initial_dialog_id = WaterfallDialog.__name__

    async def first_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for destination."""
        card_details = step_context.options

        food_card = self.create_adaptive_card_attachment()
        response = self.create_response(step_context.context.activity, food_card)
        await step_context.context.send_activity(response)
        await step_context.context.send_activity('Card')

        if step_context.context.activity.value is None:
            return DialogTurnResult(DialogTurnStatus.Waiting)

        return await step_context.next(card_details)

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        card_value = step_context.context.activity.value

        message = ' '.join('{}: {}'.format(key, value) for key, value in card_value.items())

        msg = (
            f"Please confirm: { message }"

        )

        print(msg)

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types

    def create_response(self, activity: Activity, attachment: Attachment):
        """Create an attachment message response."""
        response = create_activity_reply(activity)
        response.attachments = [attachment]
        return response

    # Load attachment from file.
    def create_adaptive_card_attachment(self):
        """Create an adaptive card."""
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "json/foodCard.json")
        with open(path) as card_file:
            card = json.load(card_file)

        return Attachment(content_type="application/vnd.microsoft.card.adaptive", content=card)
