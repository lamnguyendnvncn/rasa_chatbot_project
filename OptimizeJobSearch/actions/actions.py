# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import pandas as pd

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

        #take input of job category from latest entity
        #if user change the job category save that value
        #if user did not mention job category in latest entity, take value from slot
        #if slot is empty, take the value of the latest entity.
        #everything goes the same with job location
        job_type=next(tracker.get_latest_entity_values("job_category"),None)
        if job_type!=None and job_type!=tracker.get_slot("category"):
            pass
        else:
            job_type=tracker.get_slot("category")
            if not job_type:
                job_type=next(tracker.get_latest_entity_values("job_category"),None)
        
        job_place=next(tracker.get_latest_entity_values("job_location"),None)
        if job_place!=None and job_place!=tracker.get_slot("location"):
            pass
        else:
            job_place=tracker.get_slot("location")
            if not job_place:
                job_place=next(tracker.get_latest_entity_values("job_location"),None)
        dispatcher.utter_message(text=f"Received job category: {job_type}, job location: {job_place}.\n")
        #if there's no entity values in both latest entities and slot return this message.
        if not job_type and not job_place:
            msg="I did not receive any information about job category and job location. Please let me know your desired job information!"
            dispatcher.utter_message(text=msg)
            return []

        #if only receive job location information from both latest entities and slot, return this message
        if not job_type and job_place:
            msg=f"I only received your job location {job_place}. Please let me know your job category!"
            dispatcher.utter_message(text=msg)
            return [SlotSet("location", job_place)]

        #if only receive job category information from both latest entities and slot, return this message
        if not job_place and job_type:
            msg=f"I only received your job category {job_type}. Please let me know your job location!"
            dispatcher.utter_message(text=msg)
            return [SlotSet("category", job_type)]

        #if have both information about job location and category, return this message.
        df=pd.read_csv('/home/lam/Downloads/intern-rasa_chatbot(my_repo)/OptimizeJobSearch/actions/db.csv')
        df1=df[df['Category']==job_type]
        target=df1[df['Location']==job_place]
        if len(target)==0:
            msg=f"Sorry! We cannot find any {job_type} position in {job_place}. We will update our career opportunities soon!"
            dispatcher.utter_message(text=msg)
            return [SlotSet("category", job_type), SlotSet("location", job_place)]
        else:
            if (target['Available'].iloc[0]=="Yes"):
                msg=f"There's job available in {job_type} position in {job_place}. You can contact {target['Contact Information'].iloc[0]} for further information! "
                dispatcher.utter_message(text=msg)
                return [SlotSet("category", job_type), SlotSet("location", job_place)]
            else:
                msg=f"There's job in {job_type} position in {job_place} but it's not available now. You can contact {target['Contact Information'].iloc[0]} for future opportunities!"
                dispatcher.utter_message(text=msg)
                return [SlotSet("category", job_type), SlotSet("location", job_place)]
