class EchoBot:
    async def on_turn(self, context):
        from_id = context.activity.from_property.id
        if context.activity.type == "message":
            await context.send_activity(f"Ты сказал - {context.activity.text}")
        elif context.activity.type == "conversationUpdate":
            if from_id == getattr(context.activity.members_added[0], "id", None):
                name = context.activity.from_property.name
                await context.send_activity(f"Привет {name}")
