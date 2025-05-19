# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import os
import asyncio
from marketing_campaign.app import graph
from marketing_campaign.state import OverallState, ConfigModel
from marketing_campaign import mailcomposer
from marketing_campaign.email_reviewer import TargetAudience
from langchain_core.runnables.config import RunnableConfig


async def main():
    print("What marketing campaign do you want to create?")
    
    target_audience = os.environ.get("TARGET_AUDIENCE")
    if not target_audience:
        target_audience = 'academic'

    inputState = OverallState(
        messages=[],
        operation_logs=[],
        has_composer_completed=False
    )
    while True:
        usermsg = input("YOU [Type OK when you are happy with the email proposed] >>> ")
        inputState.messages.append(mailcomposer.Message(content=usermsg, type=mailcomposer.Type.human))
        configurable=ConfigModel(
                recipient_email_address=os.environ["RECIPIENT_EMAIL_ADDRESS"],
                sender_email_address=os.environ["SENDER_EMAIL_ADDRESS"],
                target_audience=target_audience
            ).model_dump()
        
        configurable["thread_id"] = "thread_id"
        output = await graph.ainvoke(inputState, RunnableConfig(
            configurable=configurable
        )
)

        outputState = OverallState.model_validate(output)
        if len(outputState.operation_logs) > 0:
            print(outputState.operation_logs)
            break
        else:
            print(outputState.messages[-1].content)
        inputState = outputState


if __name__ == "__main__":
    asyncio.run(main())
