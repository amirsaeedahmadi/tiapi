# IMPORTING THE NECESSARY PACKAGES

from MessageManager import JiraMailMessage

from datetime import datetime 

# KEEP IN MIND THAT THE JiraMailMessage CLASS AUTOMATICALLY SENDS MESSAGES AFTER BEING INITIALIZED

# THE ORGANIZE FUNCTION

def Automate(DICTIONARY: dict) :

    # CHECKING FOR KEYS
    
    def KeyCheck(data : dict, keys: list, default="") -> str :
    
        """Safely fetch nested dictionary values."""
        
        for key in keys:
        
            if isinstance(data, dict) and key in data:
            
                data = data[key]
                
            else:
            
                return default
                
        return data

    # DECLARING INITIAL VARIABLES

    MessageKey = KeyCheck(DICTIONARY, ["issue", "key"])                                                                          
    MessageSummary = KeyCheck(DICTIONARY, ["issue", "fields", "summary"])
    MessageIssueType = KeyCheck(DICTIONARY, ["issue", "fields", "issuetype", "name"])
    MessageEventType = KeyCheck(DICTIONARY, ["issue_event_type_name"])
    MessageDescription = KeyCheck(DICTIONARY, ["issue", "fields", "description"])
    MessageStatus = KeyCheck(DICTIONARY, ["issue", "fields", "status", "name"])
    MessagePriority = KeyCheck(DICTIONARY, ["issue", "fields","priority","name"])
    MessageComment = KeyCheck(DICTIONARY, ["comment", "body"])
    MessageCreatorUsername = KeyCheck(DICTIONARY, ["issue", "fields", "creator", "name"])
    MessageCreatorEmail = KeyCheck(DICTIONARY, ["issue", "fields", "creator", "emailAddress"])
    MessageAssigneeUsername = KeyCheck(DICTIONARY, ["issue", "fields", "assignee", "name"]) if DICTIONARY["issue_event_type_name"] != "issue_assigned" else DICTIONARY["changelog"]["items"][0]["from"]
    MessageAssgineeEmail = KeyCheck(DICTIONARY, ["issue", "fields", "assignee", "emailAddress"]) if DICTIONARY["issue_event_type_name"] != "issue_assigned" else f"""{DICTIONARY["changelog"]["items"][0]["from"]}@darvagcloud.com"""
    MessageCommentorUsername = KeyCheck(DICTIONARY, ["comment", "author", "name"])
    MessageCommentorEmail = KeyCheck(DICTIONARY, ["comment", "author", "emailAddress"])
    MessageAssignerUsername = KeyCheck(DICTIONARY, ["user", "key"])
    MessageAssignerEmail = KeyCheck(DICTIONARY, ["user", "emailAddress"])
    MessageNewAssigneeUsername = KeyCheck(DICTIONARY, ["issue", "fields", "assignee", "name"])
    MessageNewAssigneeEmail = KeyCheck(DICTIONARY, ["issue", "fields", "assignee", "emailAddress"])
    MessageStarterUsername = KeyCheck(DICTIONARY, ["user", "key"])
    MessageStarterEmail = KeyCheck(DICTIONARY, ["user", "emailAddress"])
    MessageStopperUsername = KeyCheck(DICTIONARY, ["user", "key"])
    MessageStopperEmail = KeyCheck(DICTIONARY, ["user", "emailAddress"])
    MessageResolverUsername = KeyCheck(DICTIONARY, ["user", "key"])
    MessageResolverEmail = KeyCheck(DICTIONARY, ["user", "emailAddress"])
    MessageCloserUsername = KeyCheck(DICTIONARY, ["user", "key"])
    MessageCloserEmail = KeyCheck(DICTIONARY, ["user", "emailAddress"])

    # ASSIGNING THE INITIAL VARIABLES TO THE MESSAGE ATTRIBUTES

    Condition = str(DICTIONARY["issue_event_type_name"])

    match Condition :

        case "issue_created" : # AN ISSUE IS CREATED

            try :

                Message = JiraMailMessage(
                                          key = MessageKey,
                                          summary = MessageSummary,
                                          issue_type = MessageIssueType,
                                          event_type = MessageEventType,
                                          description = MessageDescription,
                                          status = MessageStatus,
                                          creator_username = MessageCreatorUsername,
                                          creator_email = MessageCreatorEmail,
                                          assignee_username = MessageAssigneeUsername,
                                          assignee_email = MessageAssgineeEmail,
                                          priority = MessagePriority
                                         )
            except Exception as e :

                print(f"Couldn't Construct , Log Or Send Message : {e}")

                with open("logs.txt", "a") as logfile :

                    logfile.write(f"""[ Message Construction Module ]\nErr : Couldn't Construct , Log Or Send Message : \n{e}\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n""")

                    logfile.write(f"\n")

        case "issue_commented" : # A COMMENT HAS BEEN POSTED

            try :

                Message = JiraMailMessage(
                                          key = MessageKey,
                                          summary = MessageSummary,
                                          issue_type = MessageIssueType,
                                          event_type = MessageEventType,
                                          status = MessageStatus,
                                          creator_username = MessageCreatorUsername,
                                          creator_email = MessageCreatorEmail,
                                          comment = MessageComment,
                                          commentor_username = MessageCommentorUsername,
                                          commentor_email = MessageCommentorEmail,
                                          assignee_username = MessageAssigneeUsername,
                                          assignee_email = MessageAssgineeEmail,
                                          priority = MessagePriority
                                         )
            
            except Exception as e :

                print(f"Couldn't Construct , Log Or Send Message : {e}")            

                with open("logs.txt", "a") as logfile :

                    logfile.write(f"""[ Message Construction Module ]\nErr : Couldn't Construct , Log Or Send Message : \n{e}\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n""")
                    
                    logfile.write(f"\n")

        case "issue_assigned" : # SOMEONE HAS BEEN ASSIGNED TO AN ISSUE

            try :

                Message = JiraMailMessage(
                                          key = MessageKey,
                                          summary = MessageSummary,
                                          issue_type = MessageIssueType,
                                          event_type = MessageEventType,
                                          status = MessageStatus,
                                          creator_username = MessageCreatorUsername,
                                          creator_email = MessageCreatorEmail,
                                          assignee_username = MessageAssigneeUsername,
                                          assignee_email = MessageNewAssigneeEmail,
                                          assigner_username = MessageAssignerUsername,
                                          assigner_email = MessageAssignerEmail,
                                          new_assignee_username = MessageNewAssigneeUsername,
                                          new_assignee_email = MessageNewAssigneeEmail,
                                          priority = MessagePriority
                                         )
            
            except Exception as e :

                print(f"Couldn't Construct , Log Or Send Message : {e}")

                with open("logs.txt", "a") as logfile :

                    logfile.write(f"""[ Message Construction Module ]\nErr : Couldn't Construct , Log Or Send Message : \n{e}\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n""")
                    
                    logfile.write(f"\n")

        case "issue_work_started" : # SOMEONE HAS STARTED AN ISSUE

            try :

                Message = JiraMailMessage(
                                          key = MessageKey,
                                          summary = MessageSummary,
                                          issue_type = MessageIssueType,
                                          event_type = MessageEventType,
                                          status = MessageStatus,
                                          creator_username = MessageCreatorUsername,
                                          creator_email = MessageCreatorEmail,
                                          assignee_username = MessageAssigneeUsername,
                                          assignee_email = MessageNewAssigneeEmail,
                                          starter_username = MessageStarterUsername,
                                          starter_email = MessageStarterEmail,
                                          priority = MessagePriority
                                         )
            
            except Exception as e :

                print(f"Couldn't Construct , Log Or Send Message : {e}")

                with open("logs.txt", "a") as logfile :

                    logfile.write(f"""[ Message Construction Module ]\nErr : Couldn't Construct , Log Or Send Message : \n{e}\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n""")
                    
                    logfile.write(f"\n")

        case "issue_work_stopped" : # SOMEONE HAS STOPPED AN ISSUE

            try :

                Message = JiraMailMessage(
                                          key = MessageKey,
                                          summary = MessageSummary,
                                          issue_type = MessageIssueType,
                                          event_type = MessageEventType,
                                          status = MessageStatus,
                                          creator_username = MessageCreatorUsername,
                                          creator_email = MessageCreatorEmail,
                                          assignee_username = MessageAssigneeUsername,
                                          assignee_email = MessageNewAssigneeEmail,
                                          stopper_username = MessageStopperUsername,
                                          stopper_email = MessageStopperEmail,
                                          priority = MessagePriority
                                         )
                
            except Exception as e :

                print(f"Couldn't Construct , Log Or Send Message : {e}")

                with open("logs.txt", "a") as logfile :

                    logfile.write(f"""[ Message Construction Module ]\nErr : Couldn't Construct , Log Or Send Message : \n{e}\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n""")
                    
                    logfile.write(f"\n")
            
        case "issue_resolved" : # SOMEONE HAS RESOLVED AN ISSUE

            try :

                Message = JiraMailMessage(
                                          key = MessageKey,
                                          summary = MessageSummary,
                                          issue_type = MessageIssueType,
                                          event_type = MessageEventType,
                                          status = MessageStatus,
                                          creator_username = MessageCreatorUsername,
                                          creator_email = MessageCreatorEmail,
                                          assignee_username = MessageAssigneeUsername,
                                          assignee_email = MessageNewAssigneeEmail,
                                          resolver_username = MessageResolverUsername,
                                          resolver_email = MessageResolverEmail,
                                          priority = MessagePriority
                                         )
                
            except Exception as e :

                print(f"Couldn't Construct , Log Or Send Message : {e}")

                with open("logs.txt", "a") as logfile :

                    logfile.write(f"""[ Message Construction Module ]\nErr : Couldn't Construct , Log Or Send Message : \n{e}\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n""")
                    
                    logfile.write(f"\n")

        case "issue_closed" : # SOMEONE HAS CLOSED AN ISSUE

            try :

                Message = JiraMailMessage(
                                          key = MessageKey,
                                          summary = MessageSummary,
                                          issue_type = MessageIssueType,
                                          event_type = MessageEventType,
                                          status = MessageStatus,
                                          creator_username = MessageCreatorUsername,
                                          creator_email = MessageCreatorEmail,
                                          assignee_username = MessageAssigneeUsername,
                                          assignee_email = MessageNewAssigneeEmail,
                                          closer_username = MessageCloserUsername,
                                          closer_email = MessageCloserEmail,
                                          priority = MessagePriority
                                         )

            except Exception as e :

                print(f"Couldn't Construct , Log Or Send Message : {e}")

                with open("logs.txt", "a") as logfile :

                    logfile.write(f"""[ Message Construction Module ]\nErr : Couldn't Construct , Log Or Send Message : \n{e}\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n""")
                    
                    logfile.write(f"\n")
