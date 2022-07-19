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

job_synonym={
    "artificial": "artificial intelligence",
    "nurses": "nurse",
    "drivers": "driver"
}

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
        
        
        # Preprocessing job category and job location
        #job category:
        if job_type:
            job_type=job_type.lower()
            job_type=job_synonym.get(job_type,job_type)
        #job location:
        if job_place:
            job_place=job_place.split(",")[0]
            job_place=job_place.split(" ") 
            job_place=''.join(job_place)
            job_place=job_place.lower()

        #show received job category and location:
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

        #if have both information about job location and category:
        df=pd.read_csv('/home/lam/Downloads/intern-rasa_chatbot(my_repo)/OptimizeJobSearch/actions/db.csv')
        df1=df[df['Category']==job_type]
        df2=df[df['Location']==job_place]
        target=df1[df['Location']==job_place]
        #if there's no job that has the same category and location in database, return this
        if len(target)==0:
            msg=f"Sorry! We cannot find any {job_type} position in {job_place}. We will update our career opportunities soon!"
            dispatcher.utter_message(text=msg)
            dispatcher.utter_message(text=f"There might be other job in {job_place} or {job_type} position in other place. Do you want us to check it for you?")
            return [SlotSet("category", job_type), SlotSet("location", job_place)]
        elif len(target)==1:
            #If there's jobs that satisfy category and location but not available, return this.
            if (target['Available'].iloc[0]=="Yes"):
                msg=f"There's job available in {job_type} position in {job_place}. You can contact {target['Contact Information'].iloc[0]} for further information! "
                dispatcher.utter_message(text=msg)
                return [SlotSet("category", job_type), SlotSet("location", job_place)]
            else:
                msg=f"There's job in {job_type} position in {job_place} but it's not available now. You can contact {target['Contact Information'].iloc[0]} for future opportunities!"
                dispatcher.utter_message(text=msg)
                return [SlotSet("category", job_type), SlotSet("location", job_place)]
        #If there's more than one job satisfy the requirements.
        else:
            dispatcher.utter_message(text="There are more than one job satisify your findings. Here is the list:\n")
            for i in range(len(target)):
                temp=target.iloc[i]
                msg=f"Job category: {temp['Category']}, Job location: {temp['Location']}, Availability: {temp['Available']}, Company: {temp['Company']}, Contact Information: {temp['Contact Information']} \n"
                dispatcher.utter_message(text=msg)
                return [SlotSet("category", job_type), SlotSet("location", job_place)]

confirmation_dict={
    "Yes":"yes",
    "y":"yes",
    "n":"no",
    "No":"no",
    "Y":"yes",
    "N":"no"
}

#use for see other jobs that have the same category or same location with desired job (just in case there's no job that satisfy the desired job of customer).
class ActionOtherJob(Action):

    def name(self) -> Text:
        return "action_other_job"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text,Any]) -> List[Dict[Text,Any]]:
        
        confirmation=next(tracker.get_latest_entity_values("confirm"),None)
        if not confirmation:
            msg=f"Please let us know if you still want to see other job list!"
            dispatcher.utter_message(text=msg)
            return []
        confirmation=confirmation_dict.get(confirmation,confirmation)
        if confirmation=="yes":
            job_type=tracker.get_slot("category")
            job_place=tracker.get_slot("location")
            if not job_type and not job_place:
                msg=f"You haven't gived us information about job you want to find yet!"
                dispatcher.utter_message(text=msg)
                return []

            if job_type:
                df=pd.read_csv("/home/lam/Downloads/intern-rasa_chatbot(my_repo)/OptimizeJobSearch/actions/db.csv")
                target=df[df['Category']==job_type]
                if len(target)==0:
                    msg=f"There are no {job_type} job in our database. I'm sorry for this, you can find another job!"
                    dispatcher.utter_message(text=msg)
                else:
                    msg=f"These are available {job_type} job in our database:\n"
                    dispatcher.utter_message(text=msg)
                    for i in range(len(target)):
                        temp=target.iloc[i]
                        msg=f"Job location: {temp['Location']}, Job category: {temp['Category']}, Availability: {temp['Available']}, Company: {temp['Company']}, Contact Information: {temp['Contact Information']} \n"
                        dispatcher.utter_message(text=msg)
                    dispatcher.utter_message(text="\n")

            if job_place:
                df=pd.read_csv("/home/lam/Downloads/intern-rasa_chatbot(my_repo)/OptimizeJobSearch/actions/db.csv")
                target=df[df['Location']==job_place]
                if len(target)==0:
                    msg=f"There are no job available in {job_place}. I'm so sorry for this, you can find another job!"
                    dispatcher.utter_message(text=msg)
                else:
                    msg=f"These are available jobs in {job_place}:\n"
                    dispatcher.utter_message(text=msg)
                    for i in range(len(target)):
                        temp=target.iloc[i]
                        msg=f"Job category: {temp['Category']}, Job location: {temp['Location']}, Availability: {temp['Available']}, Company: {temp['Company']}, Contact Information: {temp['Contact Information']} \n"
                        dispatcher.utter_message(text=msg)
            return []
        else:
            msg="Ok. You can find another job!"
            dispatcher.utter_message(text=msg)
            return []

from rasa_sdk.events import ConversationPaused, ConversationResumed
from rasa.utils.common import logger

class PauseConversation(Action):
    def name(self) -> Text:
        return "pause_conversation"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text,Any]):
        logger.info("Pausing conversation")
        sender_id=tracker.sender_id

        dispatcher.utter_message(f"Pausing this conversation with sender_id: {sender_id} ")

        dispatcher.utter_message("To resume, send this resume event to rasa shell:")

        dispatcher.utter_message("""curl --request POST
    --url 'http://localhost:5055/conversations/SENDER_ID/tracker/events?token=RASA_TOKEN'
    --header 'content-type: application/json'
    --data '[{"event": "resume}, {"event": "followup", "name": "resume_conversation"}]'
        """)

        return [ConversationPaused()]

    # def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text,Any]):
    #     return [ConversationPaused()]

class ResumeConversation(Action):
    def name(self) -> Text:
        return "resume_conversation"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text,Any]):
        logger.info("Resume conversation")

        sender_id=tracker.sender_id

        dispatcher.utter_message(f"Resume conversation with sender id: {sender_id}")

        return [ConversationResumed()]


    # def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
    #     return [ConversationResumed()]


# class ActionGoodBye(Action):

#     def name(self) -> Text:
#         return "action_good_bye"
        
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text,Any]) -> List[Dict[Text,Any]]:
        
        
#         return []
