from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import ActivityTypes

from .second_dialog import SecondDialog
from .third_dialog import ThirdDialog
from .card_dialog import CardDialog
from seconddialog_details import SecondDialogDetails
from carddialog_details import CardDialogDetails


class MainDialog(ComponentDialog):
    def __init__(self, configuration: dict, dialog_id: str = None):
        super(MainDialog, self).__init__(dialog_id or MainDialog.__name__)

        self._configuration = configuration

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(SecondDialog())
        self.add_dialog(ThirdDialog())
        self.add_dialog(CardDialog())
        self.add_dialog(WaterfallDialog("WFDialog", [self.intro_step, self.act_step, self.final_step]))

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Initial prompt."""
        return await step_context.prompt(TextPrompt.__name__, PromptOptions(
                prompt=MessageFactory.text("Чем могу помочь? "
                                           "\n 1 - первый диалог "
                                           "\n 2 - второй диалог "
                                           "\n 3 - третий диалог с адаптивной карточкой")),)

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # In this sample we only have a single Intent we are concerned with.
        # However, typically a scenario will have multiple different Intents
        # each corresponding to starting a different child Dialog.
        booking_details = (SecondDialogDetails())
        carddialog_details = (CardDialogDetails())

        if step_context.context.activity.type == ActivityTypes.message:
            text = step_context.context.activity.text.lower()

            if text == "2":
                return await step_context.begin_dialog(ThirdDialog.__name__, booking_details)
            if text == "3":
                return await step_context.begin_dialog(CardDialog.__name__, carddialog_details)


        # return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=MessageFactory.text("Шаг 2?")),)

        # Run the BookingDialog giving it whatever details we have from the
        # model.  The dialog will prompt to find out the remaining details.
        return await step_context.begin_dialog(SecondDialog.__name__, booking_details)
        # return await step_context.context.send_activity(MessageFactory.text('test'))

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete dialog.
        At this step, with details from the user, display the completed
        flight booking to the user.
        """
        # If the child dialog ("BookingDialog") was cancelled or the user failed
        # to confirm, the Result here will be null.
        if step_context.result is not None:
            # result = step_context.result

            # Now we have all the booking details call the booking service.
            # If the call to the booking service was successful tell the user.
            # time_property = Timex(result.travel_date)
            # travel_date_msg = time_property.to_natural_language(datetime.now())
            msg = (
                f"Финальный шаг"
                )
            await step_context.context.send_activity(MessageFactory.text(msg))
        else:
            await step_context.context.send_activity(MessageFactory.text("Thank you."))
        return await step_context.begin_dialog(MainDialog.__name__)

