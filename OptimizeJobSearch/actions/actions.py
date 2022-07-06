# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionRememberJob(Action):

    def name(self) -> Text:
        return "action_job_remember"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        job_type=tracker.get_slot("category")
        if not job_type:
            job_type=next(tracker.get_latest_entity_values("job_category"),None)
        
        job_place=tracker.get_slot("location")
        if not job_place:
            job_place=next(tracker.get_latest_entity_values("job_location"),None)

        if not job_type and not job_place:
            msg="I did not receive any information about job category and job location. Please let me know your desired job information!"
            dispatcher.utter_message(text=msg)
            return []

        if not job_type and job_place:
            msg=f"I only received your job location {job_place}. Please let me know your job category!"
            dispatcher.utter_message(text=msg)
            return [SlotSet("location", job_place)]

        if not job_place and job_type:
            msg=f"I only received your job category {job_type}. Please let me know your job location!"
            dispatcher.utter_message(text=msg)
            return [SlotSet("category", job_type)]

        msg=f"I recorded that you looking for jobs in position {job_type} and in {job_place}. But unfortunately, we don't have any available postions according to your request. Please return back in other time to see new updates!"
        dispatcher.utter_message(text=msg)
        return [SlotSet("category", job_type), SlotSet("location", job_place)]


